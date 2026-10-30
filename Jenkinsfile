pipeline {
    agent any

    environment {
        BASE_URL = credentials('Project_BaseURL')
        PLAYWRIGHT_HTML_OPEN = 'never'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat 'npm install'
                bat 'npx playwright install'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'npx playwright test --reporter=html'
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('playwright-report/index.html')) {
                    publishHTML(target: [
                        reportDir: 'playwright-report',
                        reportFiles: 'index.html',
                        reportName: 'Playwright HTML Report',
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        allowMissing: false
                    ])
                } else {
                    echo 'HTML report was not generated. Check the earlier error.'
                }
            }
        }
    }
}