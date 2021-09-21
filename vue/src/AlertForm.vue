<template>
  <b-container id="alert-form">
    <b-tabs content-class="mt-2">
      <b-tab title="Structured Alert" active>
        <b-form>
          <b-form-group label="Select topic">
            <b-form-select id="alert-topic" v-model="form.topic" :options="topics" />
          </b-form-group>
          <b-form-group label="Alert title">
            <b-form-input id="alert-title" v-model="form.title" placeholder="Enter title" type="text" />
          </b-form-group>
          <b-form-group label="Alert date">
            <b-form-input id="alert-date" v-model="form.date" placeholder="Enter date" type="date" />
          </b-form-group>
          <b-form-group label="Alert time">
            <b-form-input id="alert-time" v-model="form.time" placeholder="Enter time" type="time" />
          </b-form-group>
          <b-form-group label="Author">
            <b-form-input id="alert-author" v-model="form.author" placeholder="Enter author" type="text" />
          </b-form-group>
          <b-form-group label="Author email">
            <b-form-input id="alert-author-email" v-model="form.author_email" placeholder="Enter author email" type="email" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-right-ascension" v-model="form.right_ascension" placeholder="Enter right ascension" type="number" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-declination" v-model="form.declination" placeholder="Enter declination" type="number" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-text" v-model="form.text" placeholder="Enter alert text" type="text" />
          </b-form-group>
          <b-button @click="onSubmitAlert" variant="primary">Submit</b-button>
        </b-form>
      </b-tab>
      <b-tab title="GCN Circular">
        <b-form @submit="onSubmitAlert">
          <b-form-group label="Alert date:">
            <b-form-input id="alert-date" v-model="gcn_circular_form.date" placeholder="Date" type="datetime" />
          </b-form-group>
          <b-form-group label="From:">
            <b-form-input id="alert-from" v-model="gcn_circular_form.from" placeholder="From" type="text" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-number" v-model="gcn_circular_form.number" placeholder="Enter number" type="number" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-subject" v-model="gcn_circular_form.subject" placeholder="Enter subject" type="text" />
          </b-form-group>
          <b-form-group>
            <b-form-input id="alert-body" v-model="gcn_circular_form.body" placeholder="Enter alert body" type="text" />
          </b-form-group>
          <b-button type="submit" variant="primary">Submit</b-button>
        </b-form>
      </b-tab>
    </b-tabs>
  </b-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AlertForm',
  components: {
  },
  data() {
    return {
      form: {
        topic: '',
        date: '',
        time: '',
        title: '',
        author: '',
        author_email: '',
        right_ascension: '',
        declination: '',
        text: '',
      },
      gcn_circular_form: {
        topic: 'gcn-circular',
        body: '',
        date: '',
        from: '',
        title: 'GCN CIRCULAR',
        number: '',
        subject: '',
      },
      topics: []
    }
  },
  mounted() {
    axios
      .get(`http://skip.dev.hop.scimma.org/api/v2/topics/`)
      .then(response => {
        this.topics = response['data']['results'].map(topic => (
          {value: topic.name, text: topic.name}
        ));
      })
      .catch(error => {
        console.log(`Unable to retrieve topics: ${error}`);
      });
  },
  props: {
  },
  methods: {
    onSubmitAlert() {
      console.log('on submit alert');
      axios
        .post(`http://localhost:8000/api/alerts/submit/`, this.form)
        .then(response => {
          console.log(response);
        })
        .catch(error => {
          console.log(`Unable to submit alert: ${error}`);
        });
    }
  }
}
</script>

<style>
</style>