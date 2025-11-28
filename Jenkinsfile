pipeline {
  agent any
  environment {
    IMAGE_TAG = "routepulse-svc:4"
    CONTAINER_NAME = "routepulse"
    HOST_PORT = "12104"
    CONTAINER_PORT = "5000"
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Pre-check Docker') {
      steps {
        script {
          // Check docker is available
          def rc = sh(script: "docker info >/dev/null 2>&1 || echo FAIL", returnStdout:true).trim()
          if (rc == "FAIL") {
            error("Docker not available on this node. Failing pipeline.")
          } else {
            echo "Docker appears available."
          }
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh """
          docker build -t ${IMAGE_TAG} .
        """
      }
    }

    stage('Stop old container (if any)') {
      steps {
        // Stop and remove previous container if exists
        sh """
          if [ \$(docker ps -a --filter "name=${CONTAINER_NAME}" --format '{{.Names}}' | wc -l) -gt 0 ]; then
            docker rm -f ${CONTAINER_NAME} || true
          fi
        """
      }
    }

    stage('Run container') {
      steps {
        sh """
          docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE_TAG}
          # wait a moment for flask to start
          sleep 2
        """
      }
    }

    stage('Verify service') {
      steps {
        // show container list and test curl
        sh """
          echo "=== docker ps ==="
          docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Ports}}"
          echo
          echo "=== curl http://localhost:${HOST_PORT}/ ==="
          curl -sS --max-time 5 http://localhost:${HOST_PORT}/ || (echo "Failed to fetch HTTP response" && exit 1)
        """
      }
    }
  }

  post {
    success {
      echo "Pipeline successful — image ${IMAGE_TAG} running as ${CONTAINER_NAME} on port ${HOST_PORT}"
    }
    failure {
      echo "Pipeline failed. Check the logs above for errors."
    }
  }
}
