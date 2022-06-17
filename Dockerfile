# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.7-slim

ARG RM_DEV_SL_TOKEN=local
ARG IS_PR=""
ARG TARGET_BRANCH=""
ARG LATEST_COMMIT=""
ARG PR_NUMBER=""
ARG TARGET_REPO_URL=""

ENV RM_DEV_SL_TOKEN ${RM_DEV_SL_TOKEN}
ENV IS_PR ${IS_PR}
ENV TARGET_BRANCH ${TARGET_BRANCH}
ENV LATEST_COMMIT ${LATEST_COMMIT}
ENV PR_NUMBER ${PR_NUMBER}
ENV TARGET_REPO_URL ${TARGET_REPO_URL}

RUN echo "========================================================="
RUN echo "targetBranch: ${TARGET_BRANCH}"
RUN echo "latestCommit: ${LATEST_COMMIT}"
RUN echo "pullRequestNumber ${PR_NUMBER}"
RUN echo "repositoryUrl ${TARGET_REPO_URL}"
RUN echo "========================================================="

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
    wget

RUN python -V

# download the grpc health probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.7 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

WORKDIR /email_server

# add files into working directory
COPY . .

RUN apt-get install -qq -y build-essential
RUN apt-get install -qq  -y libffi-dev
RUN apt-get install -qq  -y git
RUN pip install sealights-python-agent

RUN if [[ $IS_PR -eq 0 ]]; then \
    echo "Check-in to repo"; \
    BUILD_NAME=$(date +%F_%T) && sl-python config --token $RM_DEV_SL_TOKEN --appname "emailservice" --branchname master --buildname "${BUILD_NAME}" --exclude "*venv*" --scm none ; \    
else \ 
    echo "Pull request"; \
    BUILD_NAME=$(date +%F_%T) && sl-python prConfig --token $RM_DEV_SL_TOKEN --appname "emailservice" --targetBranch "${TARGET_BRANCH}" \
    --exclude "*venv*" --scm none --latestCommit "${LATEST_COMMIT}" --pullRequestNumber "${PR_NUMBER}" --repositoryUrl "${TARGET_REPO_URL}" ; \
fi


RUN sl-python build --token $RM_DEV_SL_TOKEN
RUN sl-python pytest --token $RM_DEV_SL_TOKEN --teststage "Unit Tests" -vv test*


EXPOSE 8080

ENTRYPOINT opentelemetry-instrument python email_server.py
