import { execSync } from 'node:child_process'
import { mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const frontendRoot = resolve(__dirname, '..')
const outputFile = resolve(frontendRoot, 'src/types/generated/openapi.ts')

mkdirSync(dirname(outputFile), { recursive: true })

const command = `openapi-typescript ../backend/openapi.json -o ${JSON.stringify(outputFile)}`
execSync(command, {
  stdio: 'inherit',
  cwd: frontendRoot,
})

// eslint-disable-next-line no-console
console.log('\n✅ OpenAPI 类型生成完成:', outputFile)
