var autoprefixer = require('gulp-autoprefixer');
var clean = require('gulp-clean');
var concat = require('gulp-concat');
var gulp = require('gulp');
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');

gulp.task('scss', function() {
    return gulp.src('scss/main.scss')
        .pipe(sass({
            style: 'expanded'
        }))
        .pipe(autoprefixer(
            'last 2 version',
            'safari 5',
            'ie 8',
            'ie 9',
            'opera 12.1',
            'ios 6',
            'android 4'
        ))
        // .pipe(minifycss())
        // .pipe(livereload(server))
        .pipe(gulp.dest('static'));
});

gulp.task('images', function() {
    return gulp.src('images/**/*')
        // .pipe(cache(imagemin({ optimizationLevel: 3, progressive: true, interlaced: true })))
        .pipe(gulp.dest('static/images'));
});

gulp.task('js', function() {
    return gulp.src('js/**/*.js')
        .pipe(jshint('.jshintrc'))
        .pipe(jshint.reporter('default'))
        .pipe(concat('main.js'))
        // .pipe(rename({ suffix: '.min' }))
        // .pipe(uglify()
        .pipe(gulp.dest('static'));
});

gulp.task('watch', function() {
    gulp.watch('scss/**/*.scss', ['scss']);
    gulp.watch('js/**/*.js', ['js']);
    gulp.watch('images/**/*', ['images']);
});

gulp.task('clean', function() {
    return gulp.src(['static/**/*', '!static/.gitkeep'], {read: false})
        .pipe(clean());
});

gulp.task('default', ['clean'], function() {
    gulp.start('scss', 'js', 'images', 'watch');
});