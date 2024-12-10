import { appendFileSync } from 'node:fs'
export function appendToGithubSummary(markdown) {
  appendFileSync(process.env.GITHUB_STEP_SUMMARY, markdown + '\n')
}
