import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
    input: './openapi.json',
    output: './src/client',

    plugins: [
        'legacy/axios',
        {
            name: '@hey-api/sdk',
            // NOTE: this doesn't allow tree-shaking
            asClass: true,
            operationId: true,
            classNameBuilder: '{{name}}Service',
            methodNameBuilder: (operation) => {
                // @ts-expect-error - operation.name is not typed in the current version of openapi-ts
                let name: string = operation.name
                // @ts-expect-error - operation.service is not typed in the current version of openapi-ts
                const service: string = operation.service

                if (service && name.toLowerCase().startsWith(service.toLowerCase())) {
                    name = name.slice(service.length)
                }

                return name.charAt(0).toLowerCase() + name.slice(1)
            },
        },
        {
            name: '@hey-api/schemas',
            type: 'json',
        },
    ],
})
