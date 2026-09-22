const { draai, suiteNaam } = require('./omgeving');
for (const suite of ['formattering', 'afgeleiden', 'toestanden', 'lezen', 'ophalen']) {
  suiteNaam(suite); require(`./${suite}.test.js`);
}
draai();
