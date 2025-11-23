# Zsh configuration file
# 기본 설정
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export EDITOR="nano"
export PAGER="less"

# 히스토리 설정
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_SAVE_NO_DUPS
setopt HIST_FIND_NO_DUPS

# 자동완성 설정
autoload -U compinit
compinit

# 유용한 별칭들
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ps='ps aux'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias top='htop'
alias tree='tree -C'

# Python 관련 별칭
alias py='python'
alias pip='pip3'
alias venv='python -m venv'
alias activate='source .venv/bin/activate'

# Git 관련 별칭
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias gd='git diff'

# Docker 관련 별칭
alias d='docker'
alias dc='docker-compose'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'

# 프로젝트 관련 별칭
alias cdapp='cd /app'
alias cdbackend='cd /app/backend'
alias cdfrontend='cd /app/frontend'

# 서버 실행/종료 관련 함수
start_server() {
    cd /app/backend
    if [ -f "app/main.py" ]; then
        echo "FastAPI 서버를 시작합니다..."
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    else
        echo "서버 파일을 찾을 수 없습니다."
    fi
}

stop_server() {
    echo "서버를 종료합니다..."
    pkill -f uvicorn 2>/dev/null || echo "실행 중인 서버가 없습니다."
}

# 프로세스 관리 함수
find_process() {
    if [ -z "$1" ]; then
        echo "사용법: find_process <프로세스명>"
        return 1
    fi
    ps aux | grep "$1" | grep -v grep
}

kill_process() {
    if [ -z "$1" ]; then
        echo "사용법: kill_process <프로세스명>"
        return 1
    fi
    pkill -f "$1"
}

# 포트 사용 확인 함수
check_port() {
    if [ -z "$1" ]; then
        echo "사용법: check_port <포트번호>"
        return 1
    fi
    lsof -i :$1 2>/dev/null || netstat -tlnp | grep :$1
}

# 프롬프트 설정
autoload -U colors && colors
PROMPT='%F{green}%n@%m%f:%F{blue}%~%f$ '

# 자동완성 설정
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# 키 바인딩
bindkey '^R' history-incremental-search-backward
bindkey '^S' history-incremental-search-forward

# 환경 변수 (한글 입력 문제 해결)
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
export TERM=xterm-256color

# 환영 메시지
echo "🚀 Zsh 환경이 설정되었습니다!"
echo "사용 가능한 명령어:"
echo "  start_server  - FastAPI 서버 시작"
echo "  stop_server   - 서버 종료"
echo "  find_process  - 프로세스 찾기"
echo "  kill_process  - 프로세스 종료"
echo "  check_port    - 포트 사용 확인"
