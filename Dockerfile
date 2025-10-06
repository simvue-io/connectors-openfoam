# To add a new image to the Github container registry:
#   - Go to your Github account -> Account Settings -> Developer settings
#   - Create a personal access token, with access to read:packages, write:packages, and delete:packages
#   - Copy the personal access token somewhere (you will not be able to access it again)
#   - Log into the Github Docker registry using docker login ghcr.io -u <your username> -p <your access token>
#   - Build the docker container with sudo docker build -t ghcr.io/simvue-io/openfoam_example:latest -f Dockerfile  . --no-cache
#   - Check that you can correctly run the container: sudo docker run -it ghcr.io/simvue-io/openfoam_example:latest
#   - Exit the contaner with Ctrl D
#   - Push the container into the registry: docker push ghcr.io/simvue-io/openfoam_example:latest

FROM openfoam/openfoam10-paraview56

USER root
RUN apt-get update && apt-get install -y pip git vim nano

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN pip install uv

RUN git clone https://github.com/simvue-io/connectors-openfoam
WORKDIR /home/openfoam/connectors-openfoam
RUN uv venv --python 3.11
RUN uv pip install .

ENV VIRTUAL_ENV=/home/openfoam/connectors-openfoam/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN cp -r /opt/openfoam10/tutorials/incompressible/pimpleFoam/laminar/movingCone/ ./examples && \
    cp -r /opt/openfoam10/tutorials/heatTransfer/buoyantFoam/hotRoom/ ./examples && \
    cp -r /opt/openfoam10/tutorials/incompressible/simpleFoam/airFoil2D/ ./examples
