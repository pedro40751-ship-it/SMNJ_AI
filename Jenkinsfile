pipeline {
  agent none

  stages {

    stage ('Build docker image') {
      agent { label 'linux' }
      steps {
        script {
          dockerapp = docker.build(
            "pesdro/juridicoapi:${env.BUILD_ID}",
            '-f Dockerfile .'
          )
        }
      }
    }

    stage ('Push docker image') {
      agent { label 'linux' }
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'credencialPedro') {
            dockerapp.push('latest')
            dockerapp.push("${env.BUILD_ID}")
          }
        }
      }
    }

    stage ('Deploy no kubernetes') {
      agent { label 'linux' }

      environment {
        tag_version = "${env.BUILD_ID}"
      }

      steps {
        withKubeConfig([credentialsId: 'kubeconfig']) {
          sh '''
            sed -i "s/{{tag}}/${tag_version}/g" ./k8s/deployment.yaml
            kubectl apply -f k8s/deployment.yaml
          '''
        }
      }
    }
  }
}
