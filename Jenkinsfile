agentName = "ubuntu-2110"
agentLabel = "${-> println 'Right Now the Agent Name is ' + agentName; return agentName}"
pipeline {
    environment {
        PROJECT = "adc-cali"
        APP_NAME = "adc-cali-app"
        CLUSTER = "jenkins-cd"
        CLUSTER_ZONE = "us-east1-d"
        JENKINS_CRED = "${PROJECT}"
        IMAGE_TAG = "${env.GIT_COMMIT}"
    }
    agent none
    stages {
        stage('Build&Test app') {
            agent {
                node { label agentLabel as String }
            }
            steps {
                echo "Deployment test environment from docker-compose.yml"
                sh 'chmod 777 test-environment1.sh'
                sh 'sh test-environment1.sh'
            }
        }
        stage('Container Publish') {
            agent {
                node { label agentLabel as String }
            }
            steps {
                echo "Container push to DockerHub"
                sh 'chmod 777 container-publish.sh'
                sh 'sh container-publish.sh'
                script {
                    IMAGE_TAG=sh (
                        script: 'echo -n $GIT_COMMIT',
                        returnStdout: true
                    )
                }
            }
        }
        stage('Test App form dockerHub') {
            agent {
                node { label agentLabel as String }
            }
            steps {
                echo "Deployment test environment from docker hub"
                sh 'chmod 777 test-environment2.sh'
                sh 'sh test-environment2.sh'
            }
        }
        stage('Functional tests') {
            agent {
                node { label agentLabel as String }
            }
            steps {
                echo "Deployment test environment from docker hub"
                sh 'chmod 777 functional.sh'
                sh 'sh functional.sh'
            }
        }
        stage('Deploy Developer') {
            // Developer Branches
            when {
                not { branch 'master' }
                not { branch 'canary' }
            }
            agent {
                kubernetes {
                    label 'adc-cali-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    sh("kubectl get ns ${env.BRANCH_NAME} || kubectl create ns ${env.BRANCH_NAME}")
                    sh("sed -i.bak 's#jandresh/metapub:latest#jandresh/metapub:${IMAGE_TAG}#' ./metapub/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/arxiv:latest#jandresh/arxiv:${IMAGE_TAG}#' ./arxiv/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/core:latest#jandresh/core:${IMAGE_TAG}#' ./core/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessing:latest#jandresh/preprocessing:${IMAGE_TAG}#' ./preprocessing/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/db:latest#jandresh/db:${IMAGE_TAG}#' ./db/kube/dev/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestrator:latest#jandresh/orchestrator:${IMAGE_TAG}#' ./orchestrator/kube/dev/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "${env.BRANCH_NAME}", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/dev', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment metapub --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment arxiv --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment core --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment preprocessing --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment db --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=${env.BRANCH_NAME} scale deployment orchestrator --replicas=1")
                    sh("echo http://`kubectl --namespace=${env.BRANCH_NAME} get service/orchestrator -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=${env.BRANCH_NAME} get service/db -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
                }
            }
        }
        stage('Deploy Canary') {
            // Canary branch
            when { branch 'canary' }
            agent {
                kubernetes {
                    label 'adc-cali-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps {
                container('kubectl') {
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapub:latest#jandresh/metapub:${IMAGE_TAG}#' ./metapub/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/arxiv:latest#jandresh/arxiv:${IMAGE_TAG}#' ./arxiv/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/core:latest#jandresh/core:${IMAGE_TAG}#' ./core/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessing:latest#jandresh/preprocessing:${IMAGE_TAG}#' ./preprocessing/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/db:latest#jandresh/db:${IMAGE_TAG}#' ./db/kube/canary/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestrator:latest#jandresh/orchestrator:${IMAGE_TAG}#' ./orchestrator/kube/canary/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/canary', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=production scale deployment metapub --replicas=1")
                    sh("kubectl --namespace=production scale deployment arxiv --replicas=1")
                    sh("kubectl --namespace=production scale deployment core --replicas=1")
                    sh("kubectl --namespace=production scale deployment preprocessing --replicas=1")
                    sh("kubectl --namespace=production scale deployment db --replicas=1")
                    sh("kubectl --namespace=production scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=production scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=production scale deployment orchestrator --replicas=1")
                    sh("echo http://`kubectl --namespace=production get service/orchestrator -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=production get service/db -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
                }
            }
        }
        stage('Deploy Production') {
            // Production branch
            when { branch 'master' }
            agent {
                kubernetes {
                    label 'adc-cali-app'
                    defaultContainer 'jnlp'
                    yamlFile 'pod-template.yaml'
                }
            }
            steps{
                container('kubectl') {
                    sh("kubectl get ns production || kubectl create ns production")
                    sh("sed -i.bak 's#jandresh/metapub:latest#jandresh/metapub:${IMAGE_TAG}#' ./metapub/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/arxiv:latest#jandresh/arxiv:${IMAGE_TAG}#' ./arxiv/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/core:latest#jandresh/core:${IMAGE_TAG}#' ./core/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/preprocessing:latest#jandresh/preprocessing:${IMAGE_TAG}#' ./preprocessing/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/db:latest#jandresh/db:${IMAGE_TAG}#' ./db/kube/production/*.yaml")
                    sh("sed -i.bak 's#jandresh/orchestrator:latest#jandresh/orchestrator:${IMAGE_TAG}#' ./orchestrator/kube/production/*.yaml")
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'metapub/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'arxiv/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'core/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'preprocessing/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'db/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/services', credentialsId: env.JENKINS_CRED, verifyDeployments: false])
                    step([$class: 'KubernetesEngineBuilder', namespace: "production", projectId: env.PROJECT, clusterName: env.CLUSTER, zone: env.CLUSTER_ZONE, manifestPattern: 'orchestrator/kube/production', credentialsId: env.JENKINS_CRED, verifyDeployments: true])
                    sh("kubectl --namespace=production scale deployment metapub --replicas=3")
                    sh("kubectl --namespace=production scale deployment arxiv --replicas=3")
                    sh("kubectl --namespace=production scale deployment core --replicas=3")
                    sh("kubectl --namespace=production scale deployment preprocessing --replicas=3")
                    sh("kubectl --namespace=production scale deployment db --replicas=3")
                    sh("kubectl --namespace=production scale deployment mysql --replicas=1")
                    sh("kubectl --namespace=production scale deployment mongo --replicas=1")
                    sh("kubectl --namespace=production scale deployment orchestrator --replicas=3")
                    sh("echo http://`kubectl --namespace=production get service/orchestrator -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5004 > url")
                    sh("echo http://`kubectl --namespace=production get service/db -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`:5001 > url")
                }
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}
