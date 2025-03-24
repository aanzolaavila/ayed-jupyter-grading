ARG PYTHON_VERSION
FROM public.ecr.aws/docker/library/python:${PYTHON_VERSION} AS build

WORKDIR /app

COPY grading/ grading/
RUN <<EOF
  # python3 -m venv venv
  # source venv/bin/activate
  python3 -m pip install pyarmor
  pyarmor gen -O build grading
  # ls -lh
  # pwd
  # exit 1
EOF

# RUN <<EOF
#   python3 -m compileall src || exit 1
#   mkdir -p /build
#   cp -v src/__pycache__/* /build
# EOF

WORKDIR /build
# RUN ls -lha /build && exit 1
# RUN python3 -V && exit 1
# EOF

FROM ubuntu:latest AS zip
WORKDIR /build
RUN apt-get update && apt-get install zip -y
COPY --from=build /app/build /build
RUN zip -r build.zip *
