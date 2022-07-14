import datetime
import random
import string
import time

from geopy.geocoders import Nominatim
from sqlalchemy import Column, Float, Integer, Interval, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# declarative_base()是sqlalchemy内部封装的一个方法，
# 通过其构造一个基类，这个基类和它的子类，可以将Python类和数据库表关联映射起来。
Base = declarative_base()

import random
import string


# random user name 8 letters
def randomword():
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(8))


# reverse the location (lan, lon) -> location detail
g = Nominatim(user_agent=randomword())


ACTIVITY_KEYS = [
    "run_id",
    "name",
    "distance",
    "moving_time",
    "type",
    "start_date",
    "start_date_local",
    "location_country",
    "summary_polyline",
    "average_heartrate",
    "average_speed",
]

# 数据库表的对应类，该类继承了基类Base
class Activity(Base):
    # 数据库表模型类通过__tablename__和表关联起来，Column表示数据表的列。
    __tablename__ = "activities"

    run_id = Column(Integer, primary_key=True)
    name = Column(String)
    distance = Column(Float)
    moving_time = Column(Interval)
    elapsed_time = Column(Interval)
    type = Column(String)
    start_date = Column(String)
    start_date_local = Column(String)
    location_country = Column(String)
    summary_polyline = Column(String)
    average_heartrate = Column(Float)
    average_speed = Column(Float)
    streak = None

    # 根据当前的Activity对象生成一个「字典」并返回
    def to_dict(self):
        out = {}
        for key in ACTIVITY_KEYS:
            attr = getattr(self, key)
            if isinstance(attr, (datetime.timedelta, datetime.datetime)):
                out[key] = str(attr)
            else:
                out[key] = attr

        if self.streak:
            out["streak"] = self.streak

        return out


# 更新或创建一个activity
def update_or_create_activity(session, run_activity):
    # 标记是否在数据库中创建了一个新的activity
    created = False
    try:
        # 从数据库中查询是否已经有该activity
        activity = (
            session.query(Activity).filter_by(run_id=int(run_activity.id)).first()
        )
        # 没有的话则构造一个activity将其添加到数据库
        if not activity:
            start_point = run_activity.start_latlng
            location_country = getattr(run_activity, "location_country", "")
            # or China for #176 to fix
            if not location_country and start_point or location_country == "China":
                try:
                    location_country = str(
                        g.reverse(f"{start_point.lat}, {start_point.lon}")
                    )
                # limit (only for the first time)
                except:
                    print("+++++++limit+++++++")
                    time.sleep(2)
                    try:
                        location_country = str(
                            g.reverse(f"{start_point.lat}, {start_point.lon}")
                        )
                    except:
                        pass

            activity = Activity(
                run_id=run_activity.id,
                name=run_activity.name,
                distance=run_activity.distance,
                moving_time=run_activity.moving_time,
                elapsed_time=run_activity.elapsed_time,
                type=run_activity.type,
                start_date=run_activity.start_date,
                start_date_local=run_activity.start_date_local,
                location_country=location_country,
                average_heartrate=run_activity.average_heartrate,
                average_speed=float(run_activity.average_speed),
                summary_polyline=run_activity.map.summary_polyline,
            )
            session.add(activity)
            created = True
        # 数据库中已经存在该activity则更新
        else:
            activity.name = run_activity.name
            activity.distance = float(run_activity.distance)
            activity.moving_time = run_activity.moving_time
            activity.elapsed_time = run_activity.elapsed_time
            activity.type = run_activity.type
            activity.average_heartrate = run_activity.average_heartrate
            activity.average_speed = float(run_activity.average_speed)
            activity.summary_polyline = run_activity.map.summary_polyline
    except Exception as e:
        print(f"something wrong with {run_activity.id}")
        print(str(e))
        pass

    return created # 返回是否创建了一个新的activity并将其添加到数据库中


# 根据指定的数据库路径初始化一个数据库
def init_db(db_path):
    # 创建连接
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    # 生成数据库表
    Base.metadata.create_all(engine)
    # 创建程序和数据库之间的会话
    session = sessionmaker(bind=engine)
    # 返回该会话
    return session()
