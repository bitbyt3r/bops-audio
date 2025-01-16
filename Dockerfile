FROM python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app
RUN uv sync
ENV X32_ADDRESS 192.168.10.143
ENV X32_PORT 10300
ENV VHUB_ADDRESS 192.168.10.172
ENV VHUB_PORT 9990
ENV VERBOSE false
#ENV CHANNEL_MAPPING 0.0:1,0.1:2,1.0:3,1.1:4,2.0:5,2.1:6,3.0:7,3.1:8,4.0:9,4.1:10,5.0:11,5.1:12,6.0:13,6.1:14,7.0:15,7.1:16,8.0:17,8.1:18,9.0:19,9.1:20,10.0:21,10.1:22,11.0:23,11.1:24,12.0:25,12.1:26,13.0:27,13.1:28,14.0:29,14.1:30,15.0:31,15.1:32
ENV CHANNEL_MAPPING 0.0:1,0.1:2,1.0:3,1.1:4,2.0:5,2.1:6,3.0:7,3.1:8,4.0:9,4.1:10,5.0:11,5.1:12,6.0:13,6.1:14,7.0:15,7.1:16
ENV INPUT_LIST 0.0,0.1,1.0,1.1,2.0,2.1,3.0,3.1,4.0,4.1,5.0,5.1,6.0,6.1,7.0,7.1,8.0,8.1,9.0,9.1,10.0,10.1,11.0,11.1,12.0,12.1,13.0,13.1,14.0,14.1,15.0,15.1,16.0,16.1,17.0,17.1,18.0,18.1,19.0,19.1

ENTRYPOINT ["uv", "run", "bops_audio"]