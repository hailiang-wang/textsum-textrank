var gulp = require('gulp')
var shell = require('gulp-shell')

gulp.task('run-tests', shell.task([
   'python summarizer.py Test.test_key_phases']))

gulp.task('watch', function(){
   gulp.watch(['./src/**/*.py'], ['run-tests']);
});

gulp.task('default',['run-tests','watch']);