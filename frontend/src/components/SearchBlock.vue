<template>
    <div class="block">
        <h3 class="center-title">
            Настройка параметров поиска
        </h3>
    
        <div class="mode-container">
            <div class="mode-title">
            Переключатель режима поиска:
            </div>

            <label>
            <input type="radio" value="AND" v-model="mode"/>
            AND - искать патенты, содержащие все выбранные фразы
            </label>

            <label>
            <input type="radio" value="OR" v-model="mode"/>
            OR - искать патенты, содержащие хотя бы одну фразу
            </label>
        </div>
    
        <hr>
            <div class="field">
                <label>Название патента</label>
                <div class="field-row">
                    <input v-model="title"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Позволяет искать патенты по названию или его части.</p>
                            <b>Примеры:</b>
                            <p>"система охлаждения" - поиск патентов с таким словосочетанием;</p>
                            <p>"лазер" - все патенты, содержащие это слово в названии;</p>
                            <p>"метод обработки данных" - поиск конкретного названия изобретения.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>Номер документа</label>
                <div class="field-row">
                    <input v-model="publication_number"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Поиск по номеру опубликованного патента.</p>
                            <b>Примеры:</b>
                            <p>RU1234567 - российский патент;</p>
                            <p>US9876543 - американский патент;</p>
                            <p>CN110203040 - китайский патент.</p>
                        </span>
                    </div>
                </div>
            </div>
        
            <div class="field">
                <label>Номер заявки</label>
                <div class="field-row">
                    <input v-model="application_number"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Позволяет найти патент по номеру поданной заявки.</p>
                            <b>Примеры:</b>
                            <p>EA201071312A;</p>
                            <p>RU2014139887/11U.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>Код страны</label>
                <div class="field-row">
                    <input v-model="country_code"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Фильтр по стране публикации патента.</p>
                            <b>Примеры:</b>
                            <p>RU - патенты Российской Федерации;</p>
                            <p>US - патенты США;</p>
                            <p>CN - патенты Китая.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>Код вида документа</label>
                <div class="field-row">
                    <input v-model="kind_code"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Тип патентного документа.</p>
                            <b>Примеры:</b>
                            <p>A;</p>
                            <p>B;</p>
                            <p>B1;</p>
                            <p>C2.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>Дата подачи заявки</label>
                <div class="field-row">
                    <input
                        v-model="filing_date"
                        placeholder="ДД.ММ.ГГГГ или ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"
                    />

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Дата подачи заявки на патент. Можно указать одну дату или диапазон.</p>
                            <b>Примеры:</b>
                            <p>"12.03.2020" - заявки, поданные в этот день;</p>
                            <p>"01.01.2019-31.12.2019" - заявки за 2019 год;</p>
                            <p>"01.06.2020-" - все заявки после этой даты;</p>
                            <p>"-01.06.2020" - все заявки до этой даты.</p>
                        </span>
                    </div>
                </div>
            </div>

            <div class="field">
                <label>Дата публикации заявк</label>
                <div class="field-row">
                    <input
                        v-model="publication_date"
                        placeholder="ДД.ММ.ГГГГ или ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"
                    />

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Дата официальной публикации патента. Можно задать одну дату или диапазон.</p>
                            <b>Примеры:</b>
                            <p>"12.03.2020" - публикации в этот день;</p>
                            <p>"01.01.2019-31.12.2019" - публикации за 2019 год;</p>
                            <p>"01.06.2020-" - все публикации после этой даты;</p>
                            <p>"-01.06.2020" - все публикации до этой даты.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>Авторы</label>
                <div class="field-row">
                    <input v-model="inventors" placeholder="через запятую"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Фильтр по фамилиям авторов изобретения. Можно указать одного или нескольких авторов.</p>
                            <b>Примеры:</b>
                            <p>"Иванов" - патенты автора Иванов;</p>
                            <p>"Иванов, Петров" - патенты с двумя авторами;</p>
                            <p>"Smith" - поиск по иностранному автору.</p>
                        </span>
                    </div>
                </div>
            </div>
    
            <div class="field">
                <label>МПК</label>
                <div class="field-row">
                    <input v-model="classifications" placeholder="через запятую"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Дочерние коды международной патентной классификации. Дочерние коды международной патентной классификации.</p>
                            <b>Примеры:</b>
                            <p>A61K31/4184;</p>
                            <p>C12N15/113;</p>
                            <p>B61D43/00.</p>
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="field">
                <label>Реферат</label>
                <div class="field-row">
                    <input v-model="abstract"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Поиск по тексту реферата патента. Используется для поиска по краткому описанию изобретения.</p>
                            <b>Примеры:</b>
                            <p>"искусственный интеллект" - патенты в области ИИ;</p>
                            <p>"аккумулятор" - патенты про батареи;</p>
                            <p>"метод диагностики" - медицинские методы.</p>
                        </span>
                    </div>
                </div>
            </div>

            <div class="field">
                <label>Формула</label>
                <div class="field-row">
                    <input v-model="claims"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Поиск по формуле изобретения. Формула содержит юридически значимое описание технического решения.</p>
                            <b>Примеры:</b>
                            <p>"способ обработки" - поиск методов;</p>
                            <p>"устройство для охлаждения" - поиск устройств;</p>
                            <p>"система управления" - поиск систем.</p>
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="field">
                <label>Описание</label>
                <div class="field-row">
                    <input v-model="description"/>

                    <div class="tooltip">
                        <img :src="questionIcon" class="tooltip-icon"/>
                        <span class="tooltip-text">
                            <p>Поиск по полному описанию патента. Используется для глубокого поиска по тексту изобретения.</p>
                            <b>Примеры:</b>
                            <p>"нейронная сеть" - патенты в области машинного обучения;</p>
                            <p>"солнечная батарея" - патенты в энергетике;</p>
                            <p>"датчик давления" - патенты по сенсорам.</p>
                        </span>
                    </div>
                </div>
            </div>
        <br>
        <button
            class="search-btn"
            @click="search"
            :disabled="searching"
        >
            {{ searching ? "Поиск..." : "Выполнить поиск" }}
        </button>
    </div>
</template>

<script setup>
    import { ref } from "vue"
    import api from "../api/api"
    import questionIcon from "/assets/question-mark-circle.svg"


    const props = defineProps({
        keywords: Array,
        sortField: String,
        sortOrder: String,
        pageSize: Number
    })

    const emit = defineEmits(["searchResults", "searchStart"])

    const mode = ref("AND")

    const title = ref("")
    const publication_number = ref("")
    const application_number = ref("")
    const country_code = ref("")
    const kind_code = ref("")

    const filing_date = ref("")
    const publication_date = ref("")

    const inventors = ref("")
    const classifications = ref("")

    const abstract = ref("")
    const claims = ref("")
    const description = ref("")

    const page = ref(1)
    const searching = ref(false)


    function convertDate(date) {
        const [day, month, year] = date.split(".")
        return `${year}-${month}-${day}`
    }


    function parseDateRange(value) {
        if (!value) return {}

        const v = value.trim()
        const dateRegex = /^\d{2}\.\d{2}\.\d{4}$/

        if (v.includes("-")) {
            const parts = v.split(/\s*-\s*/)
            const result = {}

            if (parts[0]) result.from = convertDate(parts[0])
            if (parts[1]) result.to = convertDate(parts[1])

            return result
        }

        if (!dateRegex.test(v)) {
            throw new Error("Некорректный формат даты")
        }

        const d = convertDate(v)
        return { from: d, to: d }
    }


    async function search() {
        try {
            searching.value = true
            page.value = 1
            
            const selected = props.keywords
                .filter(k => k.selected)
                .map(k => k.text)

            const filing = parseDateRange(filing_date.value)
            const publication = parseDateRange(publication_date.value)

            const payload = {
                keywords: selected,
                mode: mode.value,
                title: title.value || undefined,
                publication_number: publication_number.value || undefined,
                application_number: application_number.value || undefined,
                country_code: country_code.value || undefined,
                kind_code: kind_code.value || undefined,
                abstract: abstract.value || undefined,
                claims: claims.value || undefined,
                description: description.value || undefined,
                inventors: inventors.value
                    ? inventors.value.split(",").map(v => v.trim())
                    : undefined,
                classifications: classifications.value
                    ? classifications.value.split(",").map(v => v.trim())
                    : undefined,
                filing_date_from: filing.from,
                filing_date_to: filing.to,
                publication_date_from: publication.from,
                publication_date_to: publication.to,
                sort_field: props.sortField || undefined,
                sort_order: props.sortOrder || undefined,
                page: page.value,
                page_size: props.pageSize
            }

            emit("searchStart")

            const response = await api.post("/patents/search", payload)

            emit("searchResults", response.data, payload)
        } catch (e) {
            alert(e.message)
        } finally {
            searching.value = false
        }
    }
</script>
    
<style>
    .block{
        display:flex;
        flex-direction:column;
        gap:10px;
    }
    
    .field{
        display:flex;
        flex-direction:column;
        gap:4px;
    }
    
    .field input {
        padding:6px 8px;
        width:100%;
        max-width:720px;
        box-sizing:border-box;
    }
    
    input[type="radio"]{
        width:auto;
    }

    label{
    font-size:14px;
    }

    .field-row{
        display:flex;
        align-items:center;
        gap:10px;
        width:100%;
    }

    .mode-container{
        background:white;
        border:2px solid black;
        border-radius:10px;
        padding:10px;
    }

    .mode-container label{
        display:block;
        margin-bottom:6px;
    }

    .mode-title{
        font-weight:bold;
        margin-bottom:6px;
    }

    .tooltip{
        position:relative;
        display:flex;
        align-items:center;
        justify-content:center;

        font-size:13px;
        cursor:help;
    }

    .tooltip-icon{
        width:25px;
        height:25px;
    }

    .tooltip-text{
        position:absolute;
        bottom:140%;
        left:50%;
        transform:translateX(-50%) translateY(5px);

        background:#f6f7f3;
        color:black;

        border:1px solid black;
        border-radius:6px;

        padding:10px 12px;

        width:260px;

        font-size:14px;
        line-height:1.35;

        white-space:normal;

        opacity:0;
        pointer-events:none;

        transition:opacity 0.25s, transform 0.25s;
    }

    .tooltip-text::after{
        content:"";
        position:absolute;

        top:100%;
        left:50%;
        transform:translateX(-50%);

        border-width:6px;
        border-style:solid;

        border-color:#D2E27B transparent transparent transparent;
    }

    .tooltip:hover .tooltip-text{
        opacity:1;
        transform:translateX(-50%) translateY(0);
    }

    .search-btn{
        align-self:center;
        width:220px;
        padding:10px;
        border-radius:10px;
        font-weight:bold;
    }
</style>