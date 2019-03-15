#!/usr/bin/env groovy
// Construct tag version from pom version and pipelineId input param
def set(String version, String pipelineId) {
  if (pipelineId == "") {
			//id empty, default to jenkins build info
			echo "pipelineId is empty, defaulting to ${currentBuild.startTimeInMillis}-${currentBuild.number}"
			pipelineId = "${currentBuild.startTimeInMillis}-${currentBuild.number}"
		} else {
			echo "pipelineId is ${pipelineId}"
		}
		
		TAG_VERSION = VERSION.replace("-SNAPSHOT", "") + "-" + pipelineId
		currentBuild.displayName = "${TAG_VERSION}"
		def previousDesc = currentBuild.description
		currentBuild.description = "${previousDesc} TAG_VERSION=${TAG_VERSION}"
		stage "SetVersion|" + TAG_VERSION
}

// Uses Maven Release Plugin
// Creates SCM tag of format <artifact>-<tagVersion>
// Retains POM version of branch as <devVersion>
// <credentialId> should be Jenkins SSH credential with permissions to write to Repo 
// WARNING: when implementing auto-tagging, update CodeCloud Web Hook to filter out tag updates (i.e. add ^$ to tag filter)
def tagScm(String artifact, String devVersion, String tagVersion, String credentialId) {
	
	if (env.BRANCH_NAME == 'master') {					
		stage 'Tag SCM'
		sh "git clean -f && git reset --hard origin/${env.BRANCH_NAME}"
  						
  		//TODO - NEED TO INCREMENT VERSION SOMEWHERE OR ADD SOMETHING ABOUT BRANCH IN TAGVERSION
  		//       MASTER AND RELEASE BRANCHES COULD STEP ON EACH OTHER IF TEAMS DON'T MANAGE THE POM
  		//       VERSION ADEQUATELY

		//TODO - evaluate if we want to edit the version in the pom or just use in the tag name?
		//       need to take into account how a branch will be created from the tag and what the
		//       versioning of that branch should be, and what the auto process does with it
		//       How to handle modification of snapshot (1.0.0-SNAPSHOT) vs. release (1.0.0) versions

	
	

		// Run the maven build this is a release that keeps the development version 
		// unchanged and uses Jenkins to provide the version number uniqueness
		sh "mvn -s ${MAVEN_SETTINGS} -DreleaseVersion=${tagVersion} -DdevelopmentVersion=${devVersion} -DpushChanges=false -DlocalCheckout=true -DpreparationGoals=initialize release:prepare release:perform -B"
  						
		// push the tags (alternatively we could have pushed them to a separate
		// git repo that we then pull from and repush... the latter can be 
		// helpful in the case where you run the publish on a different node
  						
		//TODO logic needed to get credentialId and determine if https or ssh is use, to use credentials differently on push
		//withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'git_m09262', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD']]) {
		sshagent([credentialId]) {
			sh "git remote -v"
			sh "git push origin ${artifact}-${tagVersion}"
		}
  		
  		
  		// we should also release the staging repo, if we had stashed the 
  		//details of the staging repository identifier it would be easy

	} else {
		echo "version.setTag() not in branch 'master', no action performed"
	}
}

return this;