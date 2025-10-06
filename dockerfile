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

WORKDIR /home/openfoam/connectors-openfoam/examples
RUN cp -r /opt/openfoam10/tutorials/incompressible/pimpleFoam/laminar/movingCone/ . && \
    cp -r /opt/openfoam10/tutorials/heatTransfer/buoyantFoam/hotRoom/ . && \
    cp -r /opt/openfoam10/tutorials/incompressible/simpleFoam/airFoil2D/ .
