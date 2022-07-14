import datetime
import sys

import arrow
import stravalib
from gpxtrackposter import track_loader
from sqlalchemy import func

from .db import Activity, init_db, update_or_create_activity


class Generator:
    # 类构造函数
    # db_path是数据库路径
    def __init__(self, db_path):
        # 创建一个strava客户端
        self.client = stravalib.Client()
        # 数据库初始化
        self.session = init_db(db_path)

        self.client_id = ""
        self.client_secret = ""
        self.refresh_token = ""

    # 需要查看
    # 设置访问stava api的相关参数
    def set_strava_config(self, client_id, client_secret, refresh_token):
        self.client_id = client_id # 客户端ID
        self.client_secret = client_secret # 客户端密钥
        self.refresh_token = refresh_token # 访问刷新token

    # 检查参数是否正确并获得访问token
    def check_access(self):
        response = self.client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
        )
        # Update the authdata object
        # 更新授权数据
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]

        self.client.access_token = response["access_token"]
        print("Access ok")
    
    # 需要查看
    # 同步数据，force表示是否查询当前日期之前的所有activity
    def sync(self, force: bool = False):
        # 获取访问token
        self.check_access()

        print("Start syncing")
        if force:
            filters = {"before": datetime.datetime.utcnow()}
        else:
            # 查询最新的一个activity
            last_activity = self.session.query(func.max(Activity.start_date)).scalar()
            # 成功查询到最新的一个activity
            if last_activity:
                last_activity_date = arrow.get(last_activity) # activity 的日期
                last_activity_date = last_activity_date.shift(days=-7)
                # 将过滤器设置为过滤数据库中已有数据之后的数据
                filters = {"after": last_activity_date.datetime}
            else:
                # 将过滤器设置为当前日期之前的所有数据
                filters = {"before": datetime.datetime.utcnow()}
        
        # 请求所有满足条件的activity
        for run_activity in self.client.get_activities(**filters):
            if run_activity.type == "Run":
                created = update_or_create_activity(self.session, run_activity)
                if created:
                    sys.stdout.write("+")
                else:
                    sys.stdout.write(".")
                sys.stdout.flush()
        self.session.commit()

    def sync_from_gpx(self, gpx_dir):
        loader = track_loader.TrackLoader()
        tracks = loader.load_tracks(gpx_dir)
        print(f"load {len(tracks)} tracks")
        if not tracks:
            print("No tracks found.")
            return
        for t in tracks:
            created = update_or_create_activity(self.session, t.to_namedtuple())
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            sys.stdout.flush()

        self.session.commit()

    def sync_from_app(self, app_tracks):
        if not app_tracks:
            print("No tracks found.")
            return
        print("Syncing tracks '+' means new track '.' means update tracks")
        for t in app_tracks:
            created = update_or_create_activity(self.session, t)
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            sys.stdout.flush()

        self.session.commit()
    
    # 需要查看
    # 加载数据
    def load(self):
        # 从数据库中查询所有有效的activity
        activities = (
            self.session.query(Activity)
            .filter(Activity.distance > 0.1)
            .order_by(Activity.start_date_local)
        )
        activity_list = []

        streak = 0
        last_date = None
        # 将所有activity对象转为字典，然后存到一个列表中
        for activity in activities:
            # Determine running streak.
            if activity.type == "Run":
                date = datetime.datetime.strptime(
                    activity.start_date_local, "%Y-%m-%d %H:%M:%S"
                ).date()
                if last_date is None:
                    streak = 1
                elif date == last_date:
                    pass
                elif date == last_date + datetime.timedelta(days=1):
                    streak += 1
                else:
                    assert date > last_date
                    streak = 1
                activity.streak = streak
                last_date = date
                activity_list.append(activity.to_dict())

        return activity_list

    def get_old_tracks_ids(self):
        try:
            activities = self.session.query(Activity).all()
            return [str(a.run_id) for a in activities]
        except Exception as e:
            # pass the error
            print(f"something wrong with {str(e)}")
            return []
