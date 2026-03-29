<template>

    <div class="block">
    
    <h3>
    Ключевые фразы
    <span v-if="loading">(Генерируются ключевые фразы...)</span>
    </h3>
    
    <div class="keywords-container">
    
    <div
    v-for="(k,i) in localKeywords"
    :key="i"
    class="keyword-box"
    :class="{active:k.selected}"
    @click="openEditor(i)"
    >
    
    {{k.text}}
    
    </div>
    
    </div>
    
    <div class="add-row">
    
    <input v-model="newKeyword"/>
    
    <button @click="addKeyword">
    Добавить
    </button>
    
    </div>
    
    
    <!-- окно редактирования -->
    
    <div
    v-if="editorOpen"
    class="confirm-overlay"
    @click.self="editorOpen=false"
    >
    
    <div class="confirm-box">
    
    <p class="confirm-title">
    Управление ключевой фразой
    </p>
    
    <input
    v-model="editedText"
    class="edit-input"
    />
    
    <div class="confirm-buttons">
    
    <button
    class="btn-edit"
    @click="saveEdit"
    >
    Изменить
    </button>
    
    <button
    class="btn-toggle"
    @click="toggleSelected"
    >
    {{ editedKeyword?.selected ? "Исключить" : "Включить" }}
    </button>
    
    <button
    class="btn-delete"
    @click="deleteKeyword"
    >
    Удалить
    </button>
    
    </div>
    
    </div>
    
    </div>
    
    </div>
    
</template>
    
    
<script setup>
    
    import { ref, watch } from "vue"
    
    const props = defineProps({
    keywords:Array,
    loading:Boolean
    })
    
    const emit = defineEmits(["update"])
    
    const localKeywords = ref([])
    
    watch(
    () => props.keywords,
    (v)=>{
    localKeywords.value = v.map(k=>({
    text:k.text,
    selected:k.selected
    }))
    },
    {immediate:true}
    )
    
    const newKeyword = ref("")
    
    function addKeyword(){
    
    if(!newKeyword.value)
    return
    
    const copy = [
    ...localKeywords.value,
    {
    text:newKeyword.value,
    selected:false
    }
    ]
    
    localKeywords.value = copy
    
    newKeyword.value=""
    
    emit("update", copy)
    
    }
    
    
    
    const editorOpen = ref(false)
    
    const editedIndex = ref(null)
    
    const editedText = ref("")
    
    const editedKeyword = ref(null)
    
    
    
    function openEditor(i){
    
    editedIndex.value = i
    
    editedKeyword.value = localKeywords.value[i]
    
    editedText.value = localKeywords.value[i].text
    
    editorOpen.value = true
    
    }
    
    
    
    function saveEdit(){
    
    const copy = [...localKeywords.value]
    
    copy[editedIndex.value] = {
    ...copy[editedIndex.value],
    text: editedText.value
    }
    
    localKeywords.value = copy
    
    emit("update", copy)
    
    editorOpen.value = false
    
    }
    
    
    
    function toggleSelected(){
    
    const copy = [...localKeywords.value]
    
    copy[editedIndex.value] = {
    ...copy[editedIndex.value],
    selected: !copy[editedIndex.value].selected
    }
    
    localKeywords.value = copy
    
    emit("update", copy)
    
    editedKeyword.value = copy[editedIndex.value]
    
    }
    
    
    
    function deleteKeyword(){
    
    const copy = [...localKeywords.value]
    
    copy.splice(editedIndex.value,1)
    
    localKeywords.value = copy
    
    emit("update", copy)
    
    editorOpen.value = false
    
    }
    
</script>
    
    
<style>
    
    .keywords-container{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-bottom:10px;
    }
    
    .keyword-box{
    
    padding:6px 10px;
    
    border:2px solid #aaa;
    
    border-radius:6px;
    
    cursor:pointer;
    
    background:white;
    
    transition:0.2s;
    
    }
    
    .keyword-box:hover{
    background:#f5f5f5;
    }
    
    .keyword-box.active{
    border-color:red;
    }
    
    
    .add-row{
    display:flex;
    gap:6px;
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
    
    .edit-input{
    
    width:100%;
    
    padding:6px;
    
    margin-bottom:20px;
    
    }
    
    .confirm-buttons{
    
    display:flex;
    
    justify-content:space-between;
    
    gap:10px;
    
    }
    
    .btn-edit{
    
    background:#D2E27B;
    
    border:none;
    
    padding:8px 14px;
    
    border-radius:6px;
    
    cursor:pointer;
    
    }
    
    .btn-toggle{
    
    background:#E6E6E6;
    
    border:none;
    
    padding:8px 14px;
    
    border-radius:6px;
    
    cursor:pointer;
    
    }
    
    .btn-delete{
    
    background:#F57373;
    
    border:none;
    
    padding:8px 14px;
    
    border-radius:6px;
    
    cursor:pointer;
    
    }
    
</style>