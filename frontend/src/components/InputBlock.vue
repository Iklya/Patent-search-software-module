<template>

    <div class="block">
    
        <h3>Способ ввода данных</h3>
        
        <div>
        
        <label>
        <input type="radio" value="text" v-model="mode">
        Ввести текст вручную
        </label>
        
        <label>
        <input type="radio" value="file" v-model="mode">
        Прикрепить файл
        </label>
        
        <label>
        <input type="radio" value="url" v-model="mode">
        Ввести ссылку
        </label>
        
        </div>
        
        <div v-if="mode==='text'">
        
        <p>Введите текст патента</p>
        
        <textarea
        v-model="textInput"
        rows="8"
        />
        
        </div>
        
        <div
            v-if="mode==='file'"
                class="dropzone"
                @dragover.prevent
                @drop.prevent="dropFile"
                @dragenter="drag=true"
                @dragleave="drag=false"
                :class="{dragover:drag}"
                @click="fileInput.click()"
            >

            <div v-if="!fileName">
                <p>
                    Перетащите .txt файл сюда
                <br>
                    или нажмите, чтобы загрузить
                </p>

                <p class="limit">
                Максимальный размер файла: 1 MB
                </p>
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

        <div v-if="mode==='url'">
        
        <p>Введите URL</p>
        
        <input
        v-model="urlInput"
        />
        
        </div>
        
        <button
            @click="extractKeywords"
            :disabled="loading"
            >
            {{ loading ? "Генерация..." : "Извлечь ключевые фразы" }}
        </button>
        
        <div v-if="showConfirm" class="confirm-overlay" @click.self="showConfirm=false">
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
    
    const emit = defineEmits(["keywordsExtracted"])
    
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

    function extractKeywords(){
        if(props.hasKeywords){
        showConfirm.value = true
        return
        }

        runExtraction(false)
    }

    async function runExtraction(clearBefore){

        emit("start")

        loading.value = true

        try{

            let response

            if(mode.value === "text" && !textInput.value){
                alert("Введите текст")
                return
            }

            if(mode.value === "url" && !urlInput.value){
                alert("Введите ссылку")
                return
            }

            if(mode.value === "file" && !file.value){
                alert("Выберите файл")
                return
            }

            if(mode.value === "text"){

                response = await api.post(
                    "/keywords/extract-from-text",
                    textInput.value,
                    {
                        headers:{
                            "Content-Type":"text/plain"
                        }
                    }
                )

            }

            if(mode.value === "url"){

                response = await api.post(
                    "/keywords/extract-from-url",
                    { url: urlInput.value }
                )

            }

            if(mode.value === "file"){

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

        }
        catch(e){
            alert("Не удалось извлечь ключевые фразы.")
        }
        finally{
            loading.value = false
            emit("finish")
        }
    }

    function dropFile(e){
        const dropped = e.dataTransfer.files[0]

        if(!validateFile(dropped)) return

        file.value = dropped
        fileName.value = dropped.name
    }

    function uploadFile(e){
        const f = e.target.files[0]

        if(!validateFile(f)) return

        file.value = f
        fileName.value = f.name
    }

    function validateFile(f){
        if(!f.name.endsWith(".txt")){
            alert("Разрешены только .txt файлы")
            return false
        }

        if(f.size > 1024000){
            alert("Файл слишком большой (максимальный размер: 1MB)")
            return false
        }

        return true
    }

    function confirmClear(){
        showConfirm.value = false
        runExtraction(true)
    }

    function confirmKeep(){
        showConfirm.value = false
        runExtraction(false)
    }
    
</script>

<style>
    .dropzone{
    border:2px dashed #aaa;
    padding:30px;
    text-align:center;
    cursor:pointer;
    margin-top:10px;
    margin-right: 60px;
    }

    .dropzone:hover{
    background:#f5f5f5;
    }

    .dropzone.dragover{
        background:#eef6ff;
        border-color:#f0ab8b;
    }

    .limit{
    font-size:14px;
    color:#666;
    }

    .confirm-overlay{
        position:fixed;
        inset:0;
        background:rgba(0,0,0,0.2);
        display:flex;
        align-items:center;
        justify-content:center;
        z-index:1000;
    }

    .confirm-box{
        background:#ECEDCD;
        padding:20px;
        border-radius:10px;
        width:420px;
        text-align:center;
    }

    .confirm-title{
        font-weight:bold;
        margin-bottom:20px;
    }

    .confirm-buttons{
        display:flex;
        justify-content:center;
        gap:20px;
    }

    .btn-clear{
        background:#D2E27B;
        border:none;
        padding:8px 16px;
        cursor:pointer;
        border-radius:6px;
    }

    .btn-keep{
        background:#F57373;
        border:none;
        padding:8px 16px;
        cursor:pointer;
        border-radius:6px;
    }
</style>