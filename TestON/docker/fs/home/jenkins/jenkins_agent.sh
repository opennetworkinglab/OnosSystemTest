!/bin/bash
/usr/bin/java -jar agent.jar -jnlpUrl "https://$JENKINS_URL/computer/$JENKINS_NODE/jenkins-agent.jnlp" -secret $(cat secret.txt) -workDir /home/jenkins
