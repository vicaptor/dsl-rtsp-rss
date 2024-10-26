import asyncio
from executor import Executor
from pipeline_dsl import PipelineDSL

async def main():
    # Read pipeline yaml file
    with open('pipeline1.yaml', 'r') as f:
        pipeline_yaml = f.read()

    # Parse DSL
    dsl = PipelineDSL()
    dsl.load_from_yaml(pipeline_yaml)

    # Get pipeline configuration
    pipeline = dsl.pipelines['parking-lot-monitor']

    print(pipeline)

    # Create and start executor
    executor = Executor(pipeline)
    await executor.start()


if __name__ == "__main__":
    asyncio.run(main())
