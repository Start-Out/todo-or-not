import { Octokit } from "@octokit/core"

let newIssue = async function (token, owner, repo) {
    // Octokit.js
    // https://github.com/octokit/core.js#readme
    const octokit = new Octokit({
        auth: token
    })

    await octokit.request(`POST /repos/${owner}/${repo}/issues`, {
        owner: owner,
        repo: repo,
        title: 'Found a bug',
        body: 'I\'m having a problem with this.',
        assignees: [
            'octocat'
        ],
        milestone: 1,
        labels: [
            'bug'
        ],
        headers: {
            'X-GitHub-Api-Version': '2022-11-28'
        }
    })
}

