var autoprefixer = require('gulp-autoprefixer');
var browserify = require('gulp-browserify');
var clean = require('gulp-clean');
var concat = require('gulp-concat');
var gulp = require('gulp');
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');

gulp.task('scss', function() {
    return gulp.src('scss/main.scss')
        .pipe(sass({
            style: 'expanded',
            includePaths: [
                'scss',
                'node_modules/bootstrap-sass/assets/stylesheets'
            ]
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

gulp.task('templates', function() {
    return gulp.src('templates/**/*').pipe(gulp.dest('static/templates'));
});

gulp.task('js', function() {
    return gulp.src('js/index.js')
        .pipe(jshint('.jshintrc'))
        .pipe(jshint.reporter('default'))
        .pipe(browserify())
        // .pipe(rename({ suffix: '.min' }))
        // .pipe(uglify()
        .pipe(gulp.dest('static'));
});

gulp.task('watch', function() {
    gulp.watch('scss/**/*.scss', ['scss']);
    gulp.watch('js/**/*.js', ['js']);
    gulp.watch('images/**/*', ['images']);
    gulp.watch('templates/**/*', ['templates']);
});

gulp.task('clean', function() {
    return gulp.src(['static/**/*', '!static/.gitkeep'], {read: false})
        .pipe(clean());
});

gulp.task('default', ['clean'], function() {
    gulp.start('scss', 'js', 'images', 'templates', 'watch');
});