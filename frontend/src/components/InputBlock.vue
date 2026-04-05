<template>
    <div class="block">
        <h3 class="center-title">
            Выберите способ поиска патентов-аналогов
        </h3>

        <div class="mode-buttons">
            <button
                :class="['mode-btn', { active: mode === 'text' }]"
                @click="mode = 'text'"
            >
                Ввести текст вручную
            </button>

            <button
                :class="['mode-btn', { active: mode === 'file' }]"
                @click="mode = 'file'"
            >
                Прикрепить текстовый файл
            </button>

            <button
                :class="['mode-btn', { active: mode === 'url' }]"
                @click="mode = 'url'"
            >
                Ввести ссылку на патент
            </button>
        </div>

        <div class="input-label">
            <template v-if="mode === 'text'">
                Введите текст с описанием патента
            </template>

            <template v-if="mode === 'file'">
                Загрузите текстовый файл
            </template>

            <template v-if="mode === 'url'">
                Введите URL патентного документа
            </template>
        </div>

        <div v-if="mode === 'text'">
            <textarea
                v-model="textInput"
                rows="10"
                class="full-width"
            />
        </div>

        <div
            v-if="mode === 'file'"
            class="dropzone"
            @dragover.prevent
            @drop.prevent="dropFile"
            @dragenter="drag = true"
            @dragleave="drag = false"
            :class="{ dragover: drag }"
            @click="fileInput.click()"
        >
            <div v-if="!fileName" class="drop-content">
                <div class="icon">
                    <img :src="uploadIcon" class="upload-icon" />
                </div>

                <div class="drop-text">
                    Перетащите .txt файл сюда или нажмите, чтобы загрузить
                </div>

                <div class="limit">
                    Максимальный размер файла: 1 MB
                </div>
            </div>

            <div v-else>
                <p><b>Файл загружен:</b> {{ fileName }}</p>
            </div>

            <input
                type="file"
                ref="fileInput"
                hidden
                @change="uploadFile"
            />
        </div>

        <div v-if="mode === 'url'">
            <input
                v-model="urlInput"
                class="full-width url-input"
            />
        </div>

        <div class="action-row">
            <button
                @click="extractKeywords"
                :disabled="loading"
            >
                {{ loading ? "Генерация..." : "Извлечь ключевые фразы" }}
            </button>
        </div>

        <div
            v-if="showConfirm"
            class="confirm-overlay"
            @click.self="showConfirm = false"
        >
            <div class="confirm-box">
                <p class="confirm-title">
                    Очистить текущий список ключевых фраз перед извлечением новых?
                </p>

                <div class="confirm-buttons">
                    <button class="btn-clear" @click="confirmClear">
                        Очистить
                    </button>

                    <button class="btn-keep" @click="confirmKeep">
                        Нет
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref } from "vue"
    import api from "../api/api"
    import uploadIcon from "/assets/upload.svg"


    const emit = defineEmits([
        "keywordsExtracted",
        "start",
        "finish"
    ])

    const mode = ref("text")
    const textInput = ref("")
    const urlInput = ref("")
    const fileInput = ref(null)
    const file = ref(null)
    const fileName = ref("")
    const showConfirm = ref(false)
    const drag = ref(false)
    const loading = ref(false)

    const props = defineProps({
        hasKeywords: Boolean
    })


    function extractKeywords() {
        if (props.hasKeywords) {
            showConfirm.value = true
            return
        }
        runExtraction(false)
    }


    async function runExtraction(clearBefore) {
        emit("start")
        loading.value = true

        try {
            let response

            if (mode.value === "text" && !textInput.value) {
                alert("Введите текст")
                return
            }

            if (mode.value === "url" && !urlInput.value) {
                alert("Введите ссылку")
                return
            }

            if (mode.value === "file" && !file.value) {
                alert("Выберите файл")
                return
            }

            if (mode.value === "text") {
                response = await api.post(
                    "/keywords/extract-from-text",
                    textInput.value,
                    {
                        headers: {
                            "Content-Type": "text/plain"
                        }
                    }
                )
            }

            if (mode.value === "url") {
                response = await api.post(
                    "/keywords/extract-from-url",
                    { url: urlInput.value }
                )
            }

            if (mode.value === "file") {
                const form = new FormData()
                form.append("file", file.value)

                response = await api.post(
                    "/keywords/extract-from-file",
                    form
                )
            }

            emit("keywordsExtracted", {
                keywords: response.data.keywords,
                clear: clearBefore
            })
        } catch (e) {
            alert("Не удалось извлечь ключевые фразы.")
        } finally {
            loading.value = false
            emit("finish")
        }
    }


    function dropFile(e) {
        const dropped = e.dataTransfer.files[0]
        if (!validateFile(dropped)) return
        file.value = dropped
        fileName.value = dropped.name
    }


    function uploadFile(e) {
        const f = e.target.files[0]
        if (!validateFile(f)) return
        file.value = f
        fileName.value = f.name
    }


    function validateFile(f) {
        if (!f.name.endsWith(".txt")) {
            alert("Разрешены только .txt файлы")
            return false
        }

        if (f.size > 1024000) {
            alert("Файл слишком большой (максимальный размер: 1MB)")
            return false
        }

        return true
    }


    function confirmClear() {
        showConfirm.value = false
        runExtraction(true)
    }


    function confirmKeep() {
        showConfirm.value = false
        runExtraction(false)
    }
</script>

<style>
    .dropzone {
        border: 2px dashed black;
        padding: 40px;
        text-align: center;
        cursor: pointer;
        margin-top: 10px;
        background: white;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .dropzone:hover {
        background: #fafafa;
    }

    .dropzone.dragover {
        background: #eef6ff;
        border-color: #f0ab8b;
    }

    .upload-icon {
        width: 60px;
        height: 60px;
    }

    .limit {
        font-size: 14px;
        color: #666;
        font-weight: bold;
    }

    .mode-buttons {
        display: flex;
        gap: 10px;
    }

    .mode-btn {
        flex: 1;
        background: #d2e27b;
        border: 2px solid black;
        border-radius: 12px;
        padding: 10px;
        cursor: pointer;
        font-weight: bold;
    }

    .mode-btn.active {
        border: 3px solid red;
    }

    .confirm-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .confirm-box {
        background: #ecedcd;
        padding: 20px;
        border-radius: 10px;
        width: 420px;
        text-align: center;
    }

    .confirm-title {
        font-weight: bold;
        margin-bottom: 20px;
    }

    .confirm-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
    }

    .url-input {
        height: 45px;
        font-size: 16px;
        padding: 8px;
    }

    .btn-clear {
        background: #d2e27b;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        border-radius: 6px;
    }

    .btn-keep {
        background: #f57373;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        border-radius: 6px;
    }

    .center-title {
        text-align: center;
        font-weight: bold;
    }

    .input-label {
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }

    .full-width {
        width: 100%;
        box-sizing: border-box;
    }

    .action-row {
        display: flex;
        justify-content: flex-end;
    }

    .drop-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    .icon {
        font-size: 32px;
    }

    .drop-text {
        font-weight: bold;
    }
</style>