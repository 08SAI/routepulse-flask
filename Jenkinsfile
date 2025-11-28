pipeline {
  agent any

  environment {
    IMAGE = "routepulse-svc:4"
    CONTAINER = "routepulse-svc"
    PORT = "12104"
  }

  stages {
    stage('Pre-check Docker') {
      steps {
        script {
          if (isUnix()) {
            // Unix/Linux pre-check: ensure docker CLI present and daemon responds
            sh '''
              if ! command -v docker >/dev/null 2>&1; then
                echo "ERROR: docker CLI not available on PATH"; exit 2
              fi
              docker --version || { echo "ERROR: docker --version failed"; exit 3; }
              # Try to contact the daemon
              if ! docker info >/dev/null 2>&1; then
                echo "ERROR: Docker daemon not running or not accessible (docker info failed)"
                echo "Hint: ensure the Docker daemon is running (systemctl start docker), or set DOCKER_HOST to a reachable daemon."
                docker info 2>&1 | sed -n '1,200p' || true
                exit 4
              fi
              echo "Docker CLI and daemon OK."
            '''
          } else {
            // Windows pre-check: check executable and daemon with docker info
            bat '''
              where docker || (echo ERROR: docker CLI not found & exit /b 2)
              docker --version || (echo ERROR: docker --version failed & exit /b 3)
              rem Attempt to contact the Docker daemon; capture output to file for diagnostics
              docker info > docker_info.txt 2>&1 || (
                type docker_info.txt
                echo.
                echo ERROR: Docker daemon not running or not accessible (docker info failed)
                echo Hint: On Windows start Docker Desktop (or run: Start-Service com.docker.service as Administrator)
                echo Or configure DOCKER_HOST to a remote Docker daemon and set it in Jenkins credentials/environment
                exit /b 4
              )
              echo Docker CLI and daemon OK.
            '''
          }
        }
      }
    }

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build image') {
      steps {
        script {
          if (isUnix()) {
            sh "docker build -t ${IMAGE} ."
          } else {
            bat "docker build -t %IMAGE% ."
          }
        }
      }
    }

    stage('Stop & remove old container') {
      steps {
        script {
          if (isUnix()) {
            sh """
              if docker ps -a --format '{{.Names}}' | grep -w ${CONTAINER} >/dev/null 2>&1; then
                docker rm -f ${CONTAINER} || true
              fi
            """
          } else {
            bat '''
              for /f "tokens=*" %%i in ('docker ps -a --format "{{.Names}}" ^| findstr /R /C:"^%CONTAINER%$"') do (
                docker rm -f %CONTAINER% || exit /b 0
              )
            '''
          }
        }
      }
    }

    stage('Run container') {
      steps {
        script {
          if (isUnix()) {
            sh "docker run -d --name ${CONTAINER} -p ${PORT}:${PORT} ${IMAGE}"
          } else {
            bat "docker run -d --name %CONTAINER% -p %PORT%:%PORT% %IMAGE%"
          }
        }
      }
    }

    stage('Verify port') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              sleep 2
              docker ps --filter "name=${CONTAINER}" --format "table {{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"
              ss -ltnp | grep -E ":${PORT}\\s" || true
              curl -sS --max-time 5 http://127.0.0.1:${PORT}/ || { echo "ERROR: HTTP check failed"; exit 4; }
            '''
          } else {
            bat '''
              timeout /t 2 /nobreak >nul
              docker ps --filter "name=%CONTAINER%" --format "table {{.ID}}    {{.Image}}    {{.Status}}    {{.Ports}}"
              netstat -ano | findstr :%PORT% || echo WARNING: netstat did not show port
              curl -sS --max-time 5 http://127.0.0.1:%PORT% || (echo ERROR: HTTP check failed & exit /b 4)
            '''
          }
        }
      }
    }
  } // stages

  post {
    success { echo "Build finished: SUCCESS" }
    failure { echo "Build finished: FAILURE" }
  }
}

