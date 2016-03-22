FROM debian
MAINTAINER Oliver Niekrenz <oliver@niekrenz.de>
RUN apt-get update && apt-get install -y \
  locales \
  python \
  default-jre \
  unzip \
  wget
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV PYTHONIOENCODING UTF-8
RUN wget -q -O ProjectX.zip https://sourceforge.net/projects/project-x/files/project-x/ProjectX_0.91.0.00/ProjectX_0.91.0.zip/download \
  && unzip ProjectX.zip -d /opt
RUN mkdir /opt/TsDemuxer
COPY Demux.py /opt/TsDemuxer
ENTRYPOINT ["python", "/opt/TsDemuxer/Demux.py"]
CMD ["--help"]
