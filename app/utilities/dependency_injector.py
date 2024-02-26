from dependency_injector import containers, providers

class Session:
    def commit(self):
         print("Committing");

    def rollback(self):
        print("rollback");

    def roll(self):
        print("rollback");


class UserRepository:
    def __init__(self, session):
        self.session = session


class TaskRepository:
    def __init__(self, session):
        self.session = session


class Service:
    def __init__(self, uow):
        self.uow = uow

    def do_thing(self):
        with self.uow as uow:
            assert (
                uow.session
                == uow.user_repository.session
                == uow.task_repository.session
            )


class Container(containers.DeclarativeContainer):
    session = providers.Factory(Session)
    uow = providers.Factory(
        Session,
        session_factory=session.provider,
        user_repository=providers.Factory(UserRepository).provider,
        task_repository=providers.Factory(TaskRepository).provider,
    )

    service = providers.Factory(Service, uow=uow)


if __name__ == "__main__":
    container = Container()
    container.service().commit()