interface Window {
    existLoading: boolean
    lazy: number
    unique: number
    tokenRefreshing: boolean
    requests: Function[]
    eventSource: EventSource
    loadLangHandle: Record<string, any>
}

interface anyObj {
    [key: string]: any
}

type Writeable<T> = { -readonly [P in keyof T]: T[P] }
