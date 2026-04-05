<template>
    <div v-if="text">
        <div v-if="!open">  
            <button @click="open=true">
                [+] показать {{label}}
            </button>  
        </div>
        
        <div v-else>
            <button @click="open=false">
            [-] скрыть {{label}}
            </button>

            <div class="content" v-html="text"></div>
        </div>
    </div>
</template>
    
<script setup> 
    import { ref } from "vue"
   
    
    defineProps({
    text:String,
    label:String
    })
    
    const open = ref(false) 
</script>
    
<style>
    .content{
        max-height:250px;
        overflow:auto;
        margin-top:5px;
    }
</style>