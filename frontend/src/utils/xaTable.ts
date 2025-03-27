import type { FormInstance, TableColumnCtx } from 'element-plus'
import { dayjs } from 'element-plus'
import { cloneDeep, isEmpty } from 'lodash-es'
import { computed, ComputedRef, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { auth, getArrayKey } from '/@/utils/common'
import { httpStatusHandle, isSuccess } from '/@/utils/request'
import type { UseMutationReturn, UseQueryReturn } from '@pinia/colada'
import { useMutation, useQuery, useQueryCache } from '@pinia/colada'

export default class XaTable {
    // API实例
    public api: XaTableApi
    // Pinia colada userQuery key
    public queryKey: ComputedRef<any>
    // Pinia colada useQueryCache 返回值
    public queryCache: any
    // Pinia colada userQuery 返回值
    public indexQueryReturn: UseQueryReturn<unknown, Error, unknown> = {} as UseQueryReturn<unknown, Error, unknown>
    // Pinia colada useMutation 返回值
    public addMutationReturn: UseMutationReturn<any, any, any> = {} as UseMutationReturn<any, any, any>
    public editMutationReturn: UseMutationReturn<any, any, any> = {} as UseMutationReturn<any, any, any>
    public delMutationReturn: UseMutationReturn<any, any, any> = {} as UseMutationReturn<any, any, any>

    /* 表格状态-s 属性对应含义请查阅 XaTableProps 的类型定义 */
    public table: XaTableProps = reactive({
        ref: undefined,
        pk: 'id',
        remark: null,
        selection: [],
        column: [],
        query: {},
        acceptQuery: true,
        showCommonSearch: false,
        dblClickNotEditColumn: [undefined],
        expandAll: false,
        extend: {},
    })
    /* 表格状态-e */

    /* 表单状态-s 属性对应含义请查阅 XaTableFormProps 的类型定义 */
    public form: XaTableFormProps = reactive({
        ref: undefined,
        labelWidth: 160,
        operate: '',
        operateRows: [],
        items: {},
        submitLoading: false,
        defaultItems: {},
        loading: false,
        extend: {},
    })
    /* 表单状态-e */

    // XaTable前置处理函数列表（前置埋点）
    public before: XaTableBefore

    // XaTable后置处理函数列表（后置埋点）
    public after: XaTableAfter

    // 通用搜索数据
    public commonSearch: CommonSearch = reactive({
        form: {},
        fieldData: new Map(),
    })

    constructor(api: XaTableApi, table: XaTableProps, form: XaTableFormProps = {}, before: XaTableBefore = {}, after: XaTableAfter = {}) {
        this.api = api
        this.queryKey = computed(() => {
            return [this.api.queryKey, this.table.query]
        })
        this.queryCache = useQueryCache()
        this.form = Object.assign(this.form, form)
        this.table = Object.assign(this.table, table)
        this.before = before
        this.after = after
    }

    /**
     * 表格内部鉴权方法
     * 此方法在表头或表行组件内部自动调用，传递权限节点名，如：add、edit
     * 若需自定义表格内部鉴权，重写此方法即可
     */
    auth(node: string) {
        return auth(node)
    }

    /**
     * 运行前置函数
     * @param funName 函数名
     * @param args 参数
     */
    runBefore(funName: string, args: any = {}) {
        if (this.before && this.before[funName] && typeof this.before[funName] == 'function') {
            return this.before[funName]!({ ...args }) === false ? false : true
        }
        return true
    }

    /**
     * 运行后置函数
     * @param funName 函数名
     * @param args 参数
     */
    runAfter(funName: string, args: any = {}) {
        if (this.after && this.after[funName] && typeof this.after[funName] == 'function') {
            return this.after[funName]!({ ...args }) === false ? false : true
        }
        return true
    }

    /* API请求方法-s */
    // 查看
    index = () => {
        if (this.runBefore('index') === false) return
        this.indexQueryReturn = useQuery({
            key: this.queryKey,
            query: () => this.api.index({ query: this.table.query }),
            placeholderData: (previousData) => previousData,
        })
        this.runAfter('index')
    }
    // 删除
    del = (ids: string[]) => {
        if (this.runBefore('del', { ids }) === false) return
        if (this.api.del === undefined) return

        ids.forEach((id, index, array) => {
            this.delMutationReturn = useMutation({
                mutation: () => this.api.del!({ path: { [this.table.pk!]: id } }),
                onSuccess: (data, _vars, _context) => {
                    httpStatusHandle(data)
                    const status = (data as anyObj).status
                    if (status && typeof status === 'number' && isSuccess(status)) {
                        this.runAfter('del')
                    }
                },
                onError: (error) => {
                    console.error(error)
                },
                onSettled: () => {
                    if (index === array.length - 1) {
                        this.queryCache.invalidateQueries({ key: this.queryKey.value })
                    }
                },
            })
            this.delMutationReturn.mutate()
        })
    }
    // 请求编辑
    requestEdit = (row: TableRow) => {
        if (this.runBefore('requestEdit', { row }) === false) return
        this.form.loading = true
        this.form.items = { ...row }
        this.form.loading = false
        this.runAfter('requestEdit')
    }
    /* API请求方法-e */

    /**
     * 双击表格
     * @param row 行数据
     * @param column 列上下文数据
     */
    onTableDblclick = (row: TableRow, column: TableColumnCtx<TableRow>) => {
        if (!this.table.dblClickNotEditColumn!.includes('all') && !this.table.dblClickNotEditColumn!.includes(column.property)) {
            if (this.runBefore('onTableDblclick', { row, column }) === false) return
            this.toggleForm('Edit', [row])
            this.runAfter('onTableDblclick', { row, column })
        }
    }

    /**
     * 打开表单
     * @param operate 操作:Add=添加,Edit=编辑
     * @param operateIds 被操作项的数组:Add=[],Edit=[1,2,...]
     */
    toggleForm = (operate = '', operateRows: TableRow[] = []) => {
        if (this.runBefore('toggleForm', { operate, operateRows }) === false) return
        if (operate == 'Edit') {
            if (!operateRows.length) {
                return false
            }
            this.requestEdit(operateRows[0])
        } else if (operate == 'Add') {
            this.form.items = cloneDeep(this.form.defaultItems)
        }
        this.form.operate = operate
        this.form.operateRows = operateRows
        this.runAfter('toggleForm', { operate, operateRows })
    }

    /**
     * 提交表单
     * @param formEl 表单组件ref
     */
    onSubmit = (formEl: FormInstance | undefined = undefined) => {
        const operate = this.form.operate!

        if (this.runBefore('onSubmit', { formEl: formEl, operate: operate, items: this.form.items! }) === false) return

        // 表单验证通过后执行的api请求操作
        const submitCallback = () => {
            if (operate == 'Add' && typeof this.api.add == 'function') {
                this.addMutationReturn = useMutation({
                    mutation: () => this.api.add!({ body: this.form.items! }),
                    onSuccess: (data, _vars, _context) => {
                        httpStatusHandle(data)
                        const status = (data as anyObj).status
                        if (status && typeof status === 'number' && isSuccess(status)) {
                            this.toggleForm()
                            this.runAfter('onSubmit')
                        }
                    },
                    onError: (error) => {
                        console.error(error)
                    },
                    onSettled: () => {
                        // invalidate the query to refetch the new data
                        this.queryCache.invalidateQueries({ key: this.queryKey.value })
                    },
                })
                this.addMutationReturn.mutate()
            } else if (operate == 'Edit' && typeof this.api.edit == 'function') {
                this.editMutationReturn = useMutation({
                    mutation: () => this.api.edit!({ path: { [this.table.pk!]: this.form.operateRows![0][this.table.pk!] }, body: this.form.items! }),
                    onSuccess: (data, _vars, _context) => {
                        httpStatusHandle(data)
                        const status = (data as anyObj).status
                        if (status && typeof status === 'number' && isSuccess(status)) {
                            this.form.operateRows?.shift()
                            if (this.form.operateRows!.length > 0) {
                                this.toggleForm('Edit', this.form.operateRows)
                            } else {
                                this.toggleForm()
                            }
                            this.runAfter('onSubmit')
                        }
                    },
                    onError: (error) => {
                        console.error(error)
                    },
                    onSettled: () => {
                        // invalidate the query to refetch the new data
                        this.queryCache.invalidateQueries({ key: this.queryKey.value })
                    },
                })
                this.editMutationReturn.mutate()
            }
        }

        if (formEl) {
            this.form.ref = formEl
            formEl.validate((valid: boolean) => {
                if (valid) {
                    submitCallback()
                }
            })
        } else {
            submitCallback()
        }
    }

    /**
     * 获取表格选择项的id数组
     */
    getSelectionIds() {
        const ids: string[] = []
        this.table.selection?.forEach((item) => {
            ids.push(item[this.table.pk!])
        })
        return ids
    }

    /**
     * 表格内的事件统一响应
     * @param event 事件:selection-change=选中项改变,sort-change=排序,edit=编辑,delete=删除,field-change=单元格值改变,common-search=通用搜索
     * @param data 携带数据
     */
    onTableAction = (event: string, data: anyObj) => {
        if (this.runBefore('onTableAction', { event, data }) === false) return
        const actionFun = new Map([
            [
                'selection-change',
                () => {
                    this.table.selection = data as TableRow[]
                },
            ],
            [
                'sort-change',
                () => {
                    const newOrder: anyObj = {}
                    if (data.order_by) {
                        if (data.order_by != this.table.query!.order_by) {
                            newOrder.order_by = data.order_by
                        }
                        if (data.order_direction && data.order_direction != this.table.query!.order_direction) {
                            newOrder.order_direction = data.order_direction
                        }
                        this.table.query = Object.assign(this.table.query as anyObj, newOrder)
                    }
                },
            ],
            [
                'edit',
                () => {
                    this.toggleForm('Edit', [data.row])
                },
            ],
            [
                'delete',
                () => {
                    this.del([data.row[this.table.pk!]])
                },
            ],
            ['field-change', () => {}],
            [
                'common-search',
                () => {
                    this.table.query!.common_search = this.getCommonSearchParamValue(this.getCommonSearchData())
                },
            ],
            [
                'default',
                () => {
                    console.warn('No action defined')
                },
            ],
        ])

        const action = actionFun.get(event) || actionFun.get('default')
        action!.call(this)
        return this.runAfter('onTableAction', { event, data })
    }

    /**
     * 表格顶栏按钮事件统一响应
     * @param event 事件:refresh=刷新,edit=编辑,delete=删除,unfold=折叠/展开,change-show-column=调整列显示状态
     * @param data 携带数据
     */
    onTableHeaderAction = (event: string, data: anyObj) => {
        if (this.runBefore('onTableHeaderAction', { event, data }) === false) return
        const actionFun = new Map([
            [
                'refresh',
                () => {
                    this.indexQueryReturn.refetch()
                },
            ],
            [
                'add',
                () => {
                    this.toggleForm('Add')
                },
            ],
            [
                'edit',
                () => {
                    this.toggleForm('Edit', this.table.selection)
                },
            ],
            [
                'delete',
                () => {
                    this.del(this.getSelectionIds())
                },
            ],
            [
                'unfold',
                () => {
                    if (!this.table.ref) {
                        console.warn('Collapse/expand failed because table ref is not defined. Please assign table ref when onMounted')
                        return
                    }
                    this.table.expandAll = data.unfold
                    this.table.ref.unFoldAll(data.unfold)
                },
            ],
            [
                'change-show-column',
                () => {
                    const columnKey = getArrayKey(this.table.column, 'prop', data.field)
                    this.table.column[columnKey].show = data.value
                },
            ],
            [
                'default',
                () => {
                    console.warn('No action defined')
                },
            ],
        ])

        const action = actionFun.get(event) || actionFun.get('default')
        action!.call(this)
        return this.runAfter('onTableHeaderAction', { event, data })
    }

    /**
     * 表格初始化
     */
    mount = () => {
        if (this.runBefore('mount') === false) return

        // 记录表格的路由路径
        const route = useRoute()
        this.table.routePath = route.fullPath

        // 初始化通用搜索表单数据和字段 Map
        this.initCommonSearch()

        if (this.table.acceptQuery && !isEmpty(route.query)) {
            // 根据当前 URL 的 query 初始化通用搜索默认值
            this.setCommonSearchData(route.query)

            // 获取通用搜索数据合并至表格筛选条件
            this.table.query!.common_search = this.getCommonSearchParamValue(
                this.getCommonSearchData().concat(JSON.parse(this.table.query?.common_search ?? '[]'))
            )
        }
        this.index()
    }

    /**
     * 通用搜索初始化
     */
    initCommonSearch = () => {
        const form: anyObj = {}
        const field = this.table.column

        if (field.length <= 0) return

        for (const key in field) {
            // 关闭搜索的字段
            if (field[key].operator === false) continue

            // 取默认操作符号
            if (typeof field[key].operator == 'undefined') {
                field[key].operator = 'eq'
            }

            // 通用搜索表单字段初始化
            const prop = field[key].prop
            if (prop) {
                if (field[key].operator == 'RANGE' || field[key].operator == 'NOT RANGE') {
                    // 范围查询
                    form[prop] = ''
                    form[prop + '-start'] = ''
                    form[prop + '-end'] = ''
                } else if (field[key].operator == 'NULL' || field[key].operator == 'NOT NULL') {
                    // 复选框
                    form[prop] = false
                } else {
                    // 普通文本框
                    form[prop] = ''
                }

                // 初始化字段的通用搜索数据
                this.commonSearch.fieldData.set(prop, {
                    operator: field[key].operator,
                    render: field[key].render,
                    commonSearchRender: field[key].commonSearchRender,
                    propType: field[key].propType,
                })
            }
        }

        this.commonSearch.form = Object.assign(this.commonSearch.form, form)
    }

    /**
     * 设置通用搜索数据
     */
    setCommonSearchData = (query: anyObj) => {
        for (const key in this.table.column) {
            const prop = this.table.column[key].prop
            if (prop && typeof query[prop] !== 'undefined') {
                const queryProp = query[prop] ?? ''
                if (this.table.column[key].operator == 'RANGE' || this.table.column[key].operator == 'NOT RANGE') {
                    const range = queryProp.split(',')
                    if (this.table.column[key].render == 'datetime' || this.table.column[key].commonSearchRender == 'date') {
                        if (range && range.length >= 2) {
                            const rangeDayJs = [dayjs(range[0]), dayjs(range[1])]
                            if (rangeDayJs[0].isValid() && rangeDayJs[1].isValid()) {
                                if (this.table.column[key].commonSearchRender == 'date') {
                                    this.commonSearch.form[prop] = [rangeDayJs[0].format('YYYY-MM-DD'), rangeDayJs[1].format('YYYY-MM-DD')]
                                } else {
                                    this.commonSearch.form[prop] = [
                                        rangeDayJs[0].format('YYYY-MM-DD HH:mm:ss'),
                                        rangeDayJs[1].format('YYYY-MM-DD HH:mm:ss'),
                                    ]
                                }
                            }
                        }
                    } else {
                        this.commonSearch.form[prop + '-start'] = range[0] ?? ''
                        this.commonSearch.form[prop + '-end'] = range[1] ?? ''
                    }
                } else if (this.table.column[key].operator == 'NULL' || this.table.column[key].operator == 'NOT NULL') {
                    this.commonSearch.form[prop] = queryProp ? true : false
                } else if (this.table.column[key].render == 'datetime' || this.table.column[key].commonSearchRender == 'date') {
                    const propDayJs = dayjs(queryProp)
                    if (propDayJs.isValid()) {
                        this.commonSearch.form[prop] = propDayJs.format(
                            this.table.column[key].commonSearchRender == 'date' ? 'YYYY-MM-DD' : 'YYYY-MM-DD HH:mm:ss'
                        )
                    }
                } else {
                    this.commonSearch.form[prop] = queryProp
                }
            }
        }
    }

    /**
     * 获取通用搜索数据
     */
    getCommonSearchData = () => {
        const commonSearchData: commonSearchData[] = []

        for (const key in this.commonSearch.form) {
            if (!this.commonSearch.fieldData.has(key)) continue

            let val = null
            const fieldDataTemp = this.commonSearch.fieldData.get(key)
            if (fieldDataTemp.render == 'datetime' && (fieldDataTemp.operator == 'RANGE' || fieldDataTemp.operator == 'NOT RANGE')) {
                // 时间范围
                if (this.commonSearch.form[key] && this.commonSearch.form[key].length >= 2) {
                    if (fieldDataTemp.commonSearchRender == 'date') {
                        val = this.commonSearch.form[key][0] + ' 00:00:00' + ',' + this.commonSearch.form[key][1] + ' 23:59:59'
                    } else {
                        val = this.commonSearch.form[key][0] + ',' + this.commonSearch.form[key][1]
                    }
                }
            } else if (fieldDataTemp.operator == 'RANGE' || fieldDataTemp.operator == 'NOT RANGE') {
                // 普通的范围筛选，通用搜索初始化时已准备好 start 和 end 字段
                if (!this.commonSearch.form[key + '-start'] && !this.commonSearch.form[key + '-end']) {
                    continue
                }
                val = this.commonSearch.form[key + '-start'] + ',' + this.commonSearch.form[key + '-end']
            } else if (this.commonSearch.form[key]) {
                val = this.commonSearch.form[key]
            }

            if (val !== null) {
                if (fieldDataTemp.propType == 'number') {
                    val = parseInt(val)
                    if (typeof val !== 'number') {
                        console.warn('Value of property ' + fieldDataTemp.prop + ' is not a number')
                    }
                } else if (fieldDataTemp.propType == 'boolean') {
                    switch (val) {
                        case 'true':
                            val = true
                            break
                        case 'false':
                            val = false
                            break
                        default:
                            val = null
                            console.warn('Value of property ' + fieldDataTemp.prop + ' is not a boolean')
                    }
                }
            }

            if (val !== null) {
                commonSearchData.push({
                    field: key,
                    value: val,
                    operator: fieldDataTemp.operator,
                    render: fieldDataTemp.render,
                })
            }
        }

        return commonSearchData
    }

    /**
     * 设置通用搜索参数
     */
    getCommonSearchParamValue = (commonSearchData: commonSearchData[]) => {
        return JSON.stringify(commonSearchData)
    }
}
