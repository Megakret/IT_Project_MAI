from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, create_engine, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(unique=True, autoincrement=False, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    places: Mapped[list["UserPlace"]] = relationship(backref="user")

    __mapper_args__ = {
        "primary_key": id
    }


class Place(Base):
    __tablename__ = "place"

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(unique=True, nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "primary_key": address
    }


class UserPlace(Base):
    __tablename__ = "user_place"

    fk_user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    fk_place_address: Mapped[str] = mapped_column(ForeignKey(Place.address), nullable=False)
    score: Mapped[int] = mapped_column(CheckConstraint("score BETWEEN 1 and 10"), nullable=True)

    UniqueConstraint(fk_user_id, fk_place_address)

    __mapper_args__ = {
        "primary_key": [fk_user_id, fk_place_address]
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
        statement = select(Place).order_by(Place.name).\
            limit(places_per_page).offset((page - 1) * places_per_page)
        result = session.execute(statement).scalars().all()
    return list(result)


def rate(user_id: int, address: str, score: int, engine = engine) -> None:
    with Session(engine) as session:
        try:
            statement = update(UserPlace).\
                where(UserPlace.fk_user_id == user_id, UserPlace.fk_place_address == address).\
                values(score=score)
            session.execute(statement)
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()


def add_user_place(user_id: int, address: str, score: int | None = None, engine = engine) -> None:
    with Session(engine) as session:
        try:
            session.add(
                UserPlace(
                    fk_user_id=user_id,
                    fk_place_address=address,
                )
            )
            if (score):
                rate(user_id, address, score)
            session.flush()
        except IntegrityError:
            session.rollback()
            raise
        except:
            session.rollback()
            raise
        else:
            session.commit()


def get_user_places(page: int, places_per_page: int, user_id: int, engine=engine) -> list[UserPlace]:
    with Session(engine) as session:
        statement = select(UserPlace).where(UserPlace.fk_user_id == user_id).\
            limit(places_per_page).offset((page - 1) * places_per_page)
        result = session.execute(statement).scalars().all()
    return list(result)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
