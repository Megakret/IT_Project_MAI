from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(unique=True, autoincrement=False, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    __mapper_args__ = {
        "primary_key": id
    }


class Place(Base):
    __tablename__ = "place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(unique=True, nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "primary_key": address
    }


class Rating(Base):
    __tablename__ = "rating"

    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address), nullable=False)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    score: Mapped[int] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"), nullable=False)

    UniqueConstraint(fk_place_address, fk_user_id)

    __mapper_args__ = {
        "primary_key": [fk_place_address]
    }


engine = create_engine("sqlite:///database.db")


def add_user(id: int, name: str, email: str, engine = engine) -> None:
    with Session(engine) as session:
        try:
            session.add(
                User(
                    id=id,
                    name=name,
                    email=email,
                )
            )
            session.flush()
        except IntegrityError:
            session.rollback()
            raise # Do smth smart instead maybe
        except:
            session.rollback()
            raise # Fallback in case the're other errors
        else:
            session.commit()


def add_place(name: str, address: str, desc: str | None = None, engine = engine) -> None:
    with Session(engine) as session:
        try:
            session.add(
                Place(
                    name=name,
                    address=address,
                    desc=desc,
                )
            )
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()


"""
def add_places_all(**kwargs: str | None, engine = engine) -> None:
    with Session(engine) as session:
        try:
            (session.add_all(i) for i in args)
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except KeyError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()
"""


def get_places(page: int, places_per_page: int, engine = engine) -> list[Place]:
    with Session(engine) as session:
        query = session.query(Place).order_by(Place.name)
    query = query.limit(places_per_page).offset((page - 1) * places_per_page)
    result = query.all()
    return result


def rate(address: str, user_id: int, score: int, engine = engine) -> None:
    with Session(engine) as session:
        try:
            session.add(
                Rating(
                    fk_place_address=address,
                    fk_user_id=user_id,
                    score=score,
                )
            )
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()


def add_user_place(user_id: int, name: str, address: str, desc: str | None = None, score: int | None = None, engine = engine) -> None:
    with Session(engine) as session:
        try:
            session.add(
                Place(
                    fk_user_id=user_id,
                    name=name,
                    address=address,
                    desc=desc,
                )
            )
            if (score):
                rate(address, user_id, score)
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()


def get_user_places(page: int, places_per_page: int, user_id: int, engine=engine) -> list[Place]:
    with Session(engine) as session:
        query = session.query(Place).filter(Place.fk_user_id == user_id)
    query = query.limit(places_per_page).offset((page - 1) * places_per_page)
    result = query.all()
    return result


Base.metadata.create_all(engine)
