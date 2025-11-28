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
            // Check docker availability on Unix/Linux agent
            sh '''
              if ! command -v docker >/dev/null 2>&1; then
                echo "ERROR: docker CLI not available on PATH"; exit 2
              fi
              docker --version || { echo "ERROR: docker --version failed"; exit 3; }
            '''
          } else {
            // Windows agent
            bat '''
              where docker || (echo ERROR: docker CLI not found & exit /b 2)
              docker --version || (echo ERROR: docker --version failed & exit /b 3)
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
              if docker ps -a --format '{{.Names}}' | grep -w ${CONTAINER}; then
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
            // Wait briefly for the app to start, then check listening port and HTTP response
            sh '''
              sleep 2
              echo "=== docker ps ==="
              docker ps --filter "name=${CONTAINER}" --format "table {{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"
              echo "=== ss check ==="
              ss -ltnp | grep -E ":${PORT}\\s" || true
              echo "=== curl check ==="
              curl -sS --max-time 5 http://127.0.0.1:${PORT}/ || { echo "ERROR: HTTP check failed"; exit 4; }
            '''
          } else {
            bat '''
              timeout /t 2 /nobreak >nul
              echo === docker ps ===
              docker ps --filter "name=%CONTAINER%" --format "table {{.ID}}    {{.Image}}    {{.Status}}    {{.Ports}}"
              echo === netstat check ===
              netstat -ano | findstr :%PORT% || echo WARNING: netstat did not show port
              echo === curl check ===
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
