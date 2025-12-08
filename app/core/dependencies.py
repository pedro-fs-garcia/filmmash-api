from typing import Annotated

from fastapi import Depends

from .response import ResponseFactory, get_response_factory

ResponseFactoryDep = Annotated[ResponseFactory, Depends(get_response_factory)]
