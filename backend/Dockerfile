FROM python:3.11-slim

WORKDIR /app

# zsh 및 유용한 도구들 설치
RUN apt update && apt install -y \
    zsh \
    procps \
    net-tools \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    jq \
    lsof \
    psmisc \
    telnet \
    dnsutils \
    iputils-ping \
    sudo \
    man \
    less \
    unzip \
    locales \
    && rm -rf /var/lib/apt/lists/*

# 로케일 설정 (한글 입력 문제 해결)
RUN echo "ko_KR.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Node.js 및 npm 설치
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# zsh를 기본 셸로 설정
RUN chsh -s /usr/bin/zsh

# zsh 기본 설정은 호스트 .zshrc에서 복사됨
COPY .zshrc /root/.zshrc

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["tail", "-f", "/dev/null"]
