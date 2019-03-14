import axios from 'axios'

export default function configureAxios () {
  axios.interceptors.response.use(undefined, function (error) {
    // Log all errors in that format
    console.log(`Axios Error: ${JSON.stringify(error)}`)
    return Promise.reject(error)
  })
}
