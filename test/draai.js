const { draai, suiteNaam } = require('./omgeving');
for (const suite of ['formattering', 'afgeleiden', 'portefeuille', 'vandaag', 'grootboek', 'detail', 'toestanden', 'lezen', 'ophalen']) {
  suiteNaam(suite); require(`./${suite}.test.js`);
}
draai();
