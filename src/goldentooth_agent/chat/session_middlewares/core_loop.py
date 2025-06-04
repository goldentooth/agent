from antidote import inject
from ...pipeline import NextMiddleware, middleware
from ..session import ChatSessionContext

@middleware
@inject
async def core_loop(
  context: ChatSessionContext,
  next: NextMiddleware,
):
  while not context.should_exit:
    next_pipeline = context.next_pipeline
    if next_pipeline is None:
      break
    await next_pipeline.run(context)
  await next()

