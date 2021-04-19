var cron = require('node-cron');
var { run_tasks } = require('./tasks/task.js')
const run_cron_job = () => {
    cron.schedule('* * * * *', () => {
        try {
            run_tasks()
            console.log('running a task every minute');
        } catch (e) {
            console.log(e);
        }
    });
}
run_cron_job();
