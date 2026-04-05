<template>
    <div class="block">
        <h3 class="center-title">
            Результаты поиска патентов-аналогов
            <span v-if="loading">(Идёт поиск патентов...)</span>
        </h3>

        <div class="top-controls" v-if="totalPages > 0">
            <div class="pagination-wrapper">
                <div class="pagination">
                    <button @click="goToPage(1)">«</button>
                    <button @click="goToPage(page - 1)"><</button>

                    <span v-if="visiblePages[0] > 1"></span>

                    <span v-for="p in visiblePages" :key="p">
                        <button
                            :class="{ active: p === page }"
                            @click="goToPage(p)"
                        >
                            {{ p }}
                        </button>
                    </span>

                    <span v-if="visiblePages[visiblePages.length - 1] < totalPages"></span>

                    <button @click="goToPage(page + 1)">></button>
                    <button @click="goToPage(totalPages)">»</button>

                    <input
                        v-model="pageInput"
                        type="number"
                        min="1"
                        :max="totalPages"
                        placeholder="№"
                        class="page-input"
                        @keyup.enter="goToInputPage"
                    />

                    <button class="go-button" @click="goToInputPage">
                        <img :src="arrowRight" class="icon-btn" />
                    </button>
                </div>
            </div>

            <div class="page-size-wrapper">
                <div class="page-size">
                    <span>Отображать на странице не более</span>

                    <select
                        :value="pageSize"
                        @change="changePageSize($event)"
                    >
                        <option
                            v-for="s in pageSizes"
                            :key="s"
                            :value="s"
                        >
                            {{ s }}
                        </option>
                    </select>

                    <span>патентов</span>
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>№</th>

                    <th @click="changeSort('publication_number')">
                        Номер документа {{ arrow('publication_number') }}
                    </th>

                    <th @click="changeSort('title')">
                        Название патента {{ arrow('title') }}
                    </th>

                    <th @click="changeSort('application_number')">
                        Номер заявки {{ arrow('application_number') }}
                    </th>

                    <th @click="changeSort('country_code')">
                        Код страны {{ arrow('country_code') }}
                    </th>

                    <th @click="changeSort('kind_code')">
                        Код вида документа {{ arrow('kind_code') }}
                    </th>

                    <th @click="changeSort('filing_date')">
                        Дата подачи {{ arrow('filing_date') }}
                    </th>

                    <th @click="changeSort('publication_date')">
                        Дата публикации {{ arrow('publication_date') }}
                    </th>

                    <th>Авторы</th>
                    <th>МПК</th>
                    <th>Реферат</th>
                    <th>Формула</th>
                    <th>Описание</th>
                    <th>Ссылка</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="(r, i) in results" :key="r.patent_id || i">
                    <td>{{ (page - 1) * pageSize + i + 1 }}</td>
                    <td>{{ r.publication_number }}</td>
                    <td v-html="r.title || ''"></td>
                    <td>{{ r.application_number }}</td>
                    <td>{{ r.country_code }}</td>
                    <td>{{ r.kind_code }}</td>
                    <td>{{ r.filing_date }}</td>
                    <td>{{ r.publication_date }}</td>

                    <td>
                        {{ Array.isArray(r.inventors) ? r.inventors.join(", ") : "" }}
                    </td>

                    <td>
                        {{ Array.isArray(r.classifications) ? r.classifications.join(", ") : "" }}
                    </td>

                    <td>
                        <ExpandableText label="реферат" :text="r.abstract || ''" />
                    </td>

                    <td>
                        <ExpandableText label="формулу" :text="r.claims || ''" />
                    </td>

                    <td>
                        <ExpandableText label="описание" :text="r.description || ''" />
                    </td>

                    <td>
                        <a :href="r.source_url" target="_blank">
                            открыть
                        </a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
    import { ref, computed } from "vue"
    import ExpandableText from "./ExpandableText.vue"
    import arrowRight from "/assets/arrow-big-right.svg"


    const props = defineProps({
        results: Array,
        loading: Boolean,
        total: Number,
        page: Number,
        pageSize: Number
    })

    const emit = defineEmits(["sortChange", "pageChange", "pageSizeChange"])

    const currentSortField = ref(null)
    const currentSortOrder = ref("asc")
    const pageInput = ref("")

    const pageSizes = [5, 10, 15, 20, 40, 50, 75, 100]
    const MAX_RESULT_WINDOW = 10000

    const pageSize = computed(() => props.pageSize)

    const totalPages = computed(() => {
        if (!props.total)
            return 0

        const safeTotal = Math.min(props.total, MAX_RESULT_WINDOW)

        return Math.ceil(safeTotal / props.pageSize)
    })

    const visiblePages = computed(() => {
        const pages = []
        const maxVisible = 5

        let start = Math.max(1, props.page - 2)
        let end = Math.min(totalPages.value, props.page + 2)

        if (props.page <= 3) {
            start = 1
            end = Math.min(maxVisible, totalPages.value)
        }

        if (props.page >= totalPages.value - 2) {
            end = totalPages.value
            start = Math.max(1, totalPages.value - maxVisible + 1)
        }

        for (let i = start; i <= end; i++) {
            pages.push(i)
        }

        return pages
    })


    function goToPage(p) {
        if (p < 1 || p > totalPages.value) return
        emit("pageChange", p)
    }


    function goToInputPage() {
        const p = Number(pageInput.value)

        if (!p || p < 1 || p > totalPages.value) {
            alert("Такой страницы не существует")
            return
        }

        emit("pageChange", p)
        pageInput.value = ""
    }


    function changeSort(field) {
        if (!props.results || props.results.length === 0) return

        if (currentSortField.value !== field) {
            currentSortField.value = field
            currentSortOrder.value = "asc"
        } else {
            if (currentSortOrder.value === "asc") {
                currentSortOrder.value = "desc"
            } else if (currentSortOrder.value === "desc") {
                currentSortField.value = null
                currentSortOrder.value = null
            } else {
                currentSortOrder.value = "asc"
            }
        }

        emit("sortChange", {
            field: currentSortField.value,
            order: currentSortOrder.value
        })
    }


    function arrow(field) {
        if (currentSortField.value !== field) return ""
        if (currentSortOrder.value === "asc") return "▲"
        if (currentSortOrder.value === "desc") return "▼"
        return ""
    }


    function changePageSize(e) {
        const size = Number(e.target.value)
        emit("pageSizeChange", size)
    }
</script>

<style>
    table {
        border-collapse: collapse;
        width: 100%;
        border: 1.5pt solid black;
    }

    th,
    td {
        border: 1.5pt solid black;
        padding: 6px;
        vertical-align: top;
    }

    th {
        background: #e8ebea;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
    }

    th:hover {
        background: #dcdede;
    }

    tbody tr {
        background: white;
    }

    button {
        background: #d2e27b;
        border: 1px solid black;
        border-radius: 10px;
        padding: 10px;
        cursor: pointer;
        font-weight: bold;
    }

    .pagination {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }

    .pagination button {
        margin: 2px;
    }

    .pagination .active {
        font-weight: bold;
        background: #ddd;
    }

    .page-input {
        width: 80px;
        padding: 4px;
        margin-left: 8px;
    }

    .go-button {
        margin-left: 4px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }

    .top-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }

    .pagination-wrapper,
    .page-size-wrapper {
        background: white;
        border: 2px solid black;
        padding: 10px;
        border-radius: 12px;
    }

    .page-size {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .page-size select {
        padding: 4px;
    }

    .icon-btn {
        width: 35px;
        height: 35px;
    }
</style>