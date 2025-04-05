from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)


class Place(Base):
    __tablename__ = "place"

    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(unique=True, nullable=False)
    rate: Mapped[int] = mapped_column(CheckConstraint("rate BETWEEN 1 and 10"), nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "primary_key": address
    }


class CustomPlace(Base):
    __tablename__ = "custom_place"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    rate: Mapped[int] = mapped_column(CheckConstraint("rate BETWEEN 1 and 10"), nullable=False)
    desc: Mapped[str] = mapped_column(nullable=True)
    fk_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    UniqueConstraint(address, fk_user_id)


def add_user(name: str, email: str) -> None:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        try:
            session.add(
                User(
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


def add_place(name: str, address: str, rate: int, desc: str | None = None) -> None:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        try:
            session.add(
                Place(
                    name=name,
                    address=address,
                    rate=rate,
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


def add_places_all(data: tuple[dict[str, str | int | None]]) -> None:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        try:
            session.add_all([
                Place(
                    name=place.get('name'),
                    address=place.get('address'),
                    rate=place.get('rate'),
                    desc=place.get('desc'),
                ) for place in data])
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


def get_places(page: int, places_per_page: int) -> list[Place]:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        query = session.query(Place).order_by(Place.name)
    query = query.limit(places_per_page).offset((page - 1) * places_per_page)
    result = query.all()
    return result


def add_custom_place(name: str, address: str, rate: int, desc: str | None, user_id: int) -> None:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        try:
            session.add(
                CustomPlace(
                    name=name,
                    address=address,
                    rate=rate,
                    desc=desc,
                    fk_user_id=user_id,
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


def get_custom_places(page: int, places_per_page: int, user_id: int) -> list[CustomPlace]:
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        query = session.query(CustomPlace).filter(CustomPlace.fk_user_id == user_id).order_by(CustomPlace.id)
    query = query.limit(places_per_page).offset((page - 1) * places_per_page)
    result = query.all()
    return result


engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)
