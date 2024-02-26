from dependency_injector import containers, providers, dependencies
from loguru import logger
from app.utilities.components import MyComponent

class Container(containers.DeclarativeContainer):
    # config = providers.Configuration()

    logger = providers.Singleton(logger)
    my_component = providers.Factory(MyComponent, logger=logger)


if __name__ == "__main__":
    container = Container()

    my_component = container.my_component()
    my_component.do_something()
