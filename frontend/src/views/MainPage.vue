<template>

    <div class="container">
    
    <div class="top">
    
    <div class="left">
      <InputBlock
        :hasKeywords="keywords.length > 0"
        @keywordsExtracted="setKeywords"
        @start="keywordsLoading=true"
        @finish="keywordsLoading=false"
      />
      
      <KeywordsBlock
        :keywords="keywords"
        :loading="keywordsLoading"
        @update="updateKeywords"
      />
    </div>
    
    <div class="right">
      <SearchBlock
        :keywords="keywords"
        :sortField="sortField"
        :sortOrder="sortOrder"
        :pageSize="pageSize"
        @searchStart="onSearchStart"
        @searchResults="onSearchResults"
      />
    </div>
    
    </div>
    <ResultsBlock
      ref="resultsRef"
      :results="results"
      :loading="loading"
      :total="total"
      :page="currentPage"
      :pageSize="pageSize"
      @sortChange="onSortChange"
      @pageChange="onPageChange"
      @pageSizeChange="onPageSizeChange"
    />
    </div>
    
</template>
    
<script setup>

    import { ref, nextTick } from "vue"
    import api from "../api/api"

    import InputBlock from "../components/InputBlock.vue"
    import KeywordsBlock from "../components/KeywordsBlock.vue"
    import SearchBlock from "../components/SearchBlock.vue"
    import ResultsBlock from "../components/ResultsBlock.vue"

    const keywords = ref([])
    const results = ref([])
    const loading = ref(false)
    const keywordsLoading = ref(false)
    const resultsRef = ref(null)

    const sortField = ref(null)
    const sortOrder = ref("asc")

    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)

    const lastSearchPayload = ref(null)

    function setKeywords(data){
      const newKeywords = data.keywords.map(k=>({
        text:k,
        selected:false
      }))

      if(data.clear){
        keywords.value = newKeywords
      } else {
        keywords.value = [
          ...keywords.value,
          ...newKeywords
        ]
      }
    }

    function updateKeywords(data){
    keywords.value = data
    }

    function onSearchStart(){
    loading.value = true
    }

    async function onSearchResults(data, payload){
      try{
        results.value = data.search_result || []
        total.value = data.total || 0
        currentPage.value = data.page || 1
        pageSize.value = data.page_size || 10

        lastSearchPayload.value = payload

        await nextTick()

        resultsRef.value?.$el?.scrollIntoView({
          behavior:"smooth"
        })
      }
      finally{
        loading.value = false
      }
    }

    async function onPageChange(p){
      if (p < 1)
        return

      if (p > Math.ceil(total.value / pageSize.value))
        return

      try{
          currentPage.value = p

          const payload = {
              ...lastSearchPayload.value,
              page: p
          }

          loading.value = true

          const response = await api.post("/patents/search", payload)

          results.value = response.data.search_result
          total.value = response.data.total
      }
      catch(e){
          alert("Ошибка загрузки страницы")
          console.error(e)
      }
      finally{
          loading.value = false
      }
    }


    async function onPageSizeChange(size){
      if(!lastSearchPayload.value) return

      try{

          pageSize.value = size
          currentPage.value = 1

          const payload = {
              ...lastSearchPayload.value,
              page:1,
              page_size:size
          }

          loading.value = true

          const response = await api.post("/patents/search", payload)

          results.value = response.data.search_result
          total.value = response.data.total

          lastSearchPayload.value = payload

      }
      catch(e){
          alert("Ошибка изменения размера страницы")
      }
      finally{
          loading.value = false
      }
    }


    async function onSortChange(data){

        if(results.value.length === 0) return

        sortField.value = data.field
        sortOrder.value = data.order

        const payload = {
            ...lastSearchPayload.value,
            page: currentPage.value,
            page_size: pageSize.value
        }

        if(sortField.value){
            payload.sort_field = sortField.value
        } else {
            delete payload.sort_field
        }

        if(sortOrder.value){
            payload.sort_order = sortOrder.value
        } else {
            delete payload.sort_order
        }

        loading.value = true

        const response = await api.post("/patents/search", payload)

        results.value = response.data.search_result
        total.value = response.data.total

        lastSearchPayload.value = payload

        loading.value = false
    }

</script>
    
    <style>
    .container{
      padding:20px
    }
    
    .top{
      display:flex;
    }
    
    .left{
      width:50%;
    }
    
    .right{
      width:50%;
    }
    </style>