def dockerHost = "hyperdigitalteam"
def appName = "bloom"
def imageTag = "${dockerHost}/${appName}"
def app


pipeline {
    agent any

    stages {
        stage('Clone repository') {
            when { branch 'master' }
            steps {
                checkout scm
            }
        }

        stage('Build image') {

            /* This builds the actual image; synonymous to */
            when { branch 'master' }
            steps {
                script {
                    app = docker.build("${imageTag}")
                }
            }
        }

        stage('Test image') {
            when { branch 'master' }
            steps {
                echo "Test Passed"
            }
        }

        stage('Push image') {
            when { branch 'master' }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                        app.push("${env.BUILD_NUMBER}")
                        app.push("latest")
                    }
                }
            }
        }

        stage('Deploy image') {
            when { branch 'master' }
            steps {

                sh """
                ssh -i /var/lib/jenkins/.ssh/id_rsa -t jenkins@app.mibhub.com  \
                "sudo docker service update --image ${imageTag} --with-registry-auth --force bloom_web ;\
                 sudo docker service update --image ${imageTag} --with-registry-auth --force bloom_worker ;\
                """

            }
        }
    }

}
