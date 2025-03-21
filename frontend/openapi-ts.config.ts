import { defineConfig, defaultPlugins } from '@hey-api/openapi-ts'

export default defineConfig({
    input: './openapi.json',
    output: {
        path: 'src/client',
        format: 'prettier',
        lint: 'eslint',
    },
    plugins: [
        ...defaultPlugins,
        {
            name: '@hey-api/client-axios',
            runtimeConfigPath: './src/hey-api.ts',
        },
    ],
})
