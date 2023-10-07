// main.js (例)
document.addEventListener('DOMContentLoaded', function () {
    // 計算結果ボタンを取得
    var calculateButton = document.getElementById('calculate-button');

    // ボタンがクリックされたときの処理
    calculateButton.addEventListener('click', function () {
        // frontpageビューにリダイレクト
        window.location.href = '/frontpage';
    });
});

