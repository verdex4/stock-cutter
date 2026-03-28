// Отправка формы
document.getElementById('algorithm-form').addEventListener('submit', function(e) {
    e.preventDefault();
    console.log("Form submitted!");
    
    const formData = new FormData(this);
    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerHTML = data.result;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Добавление строки в таблицу склада
document.querySelector('.add-stock').addEventListener('click', function() {
    const table = document.querySelector('.stock tbody');
    const rows = table.querySelectorAll('tr');
    const newRowNum = rows.length + 1;
    
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="number" placeholder="Введите длину" step="any" name="stock_len${newRowNum}"></td>
        <td><input type="number" placeholder="Введите количество" name="stock_qty${newRowNum}"></td>
        <td><button class="delete-stock-row" type="button">✕</button></td>
    `;
    table.appendChild(newRow);
    
    // Добавляем обработчик для новой кнопки удаления
    newRow.querySelector('.delete-stock-row').addEventListener('click', deleteStockRow);
});

// Удаление строки из таблицы склада
function deleteStockRow(e) {
    const row = e.target.closest('tr');
    const table = document.querySelector('.stock tbody');
    const rows = table.querySelectorAll('tr');
    
    // Оставляем последнюю строку
    if (rows.length > 1) {
        row.remove();
        renameStockInputs();
    }
}

// Очистка таблицы склада
document.querySelector('.remove-stock').addEventListener('click', function() {
    const table = document.querySelector('.stock tbody');
    const rows = table.querySelectorAll('tr');
    
    // Удаляем все строки кроме первой
    for (let i = rows.length - 1; i > 0; i--) {
        rows[i].remove();
    }
    
    // Очищаем значения в первой строке
    const firstRow = table.querySelector('tr');
    firstRow.querySelector('input[name^="stock_len"]').value = '';
    firstRow.querySelector('input[name^="stock_qty"]').value = '';
    
    renameStockInputs();
});

// Переименование inputs в таблице склада
function renameStockInputs() {
    const table = document.querySelector('.stock tbody');
    const rows = table.querySelectorAll('tr');
    
    rows.forEach((row, index) => {
        const rowNum = index + 1;
        const lenInput = row.querySelector('input[name^="stock_len"]');
        const qtyInput = row.querySelector('input[name^="stock_qty"]');
        
        if (lenInput) lenInput.name = `stock_len${rowNum}`;
        if (qtyInput) qtyInput.name = `stock_qty${rowNum}`;
    });
}

// Добавление строки в таблицу заказа
document.querySelector('.add-demand').addEventListener('click', function() {
    const table = document.querySelector('.demand tbody');
    const rows = table.querySelectorAll('tr');
    const newRowNum = rows.length + 1;
    
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="number" placeholder="Введите длину" step="any" name="demand_len${newRowNum}"></td>
        <td><input type="number" placeholder="Введите количество" name="demand_qty${newRowNum}"></td>
        <td><button class="delete-demand-row" type="button">✕</button></td>
    `;
    table.appendChild(newRow);
    
    // Добавляем обработчик для новой кнопки удаления
    newRow.querySelector('.delete-demand-row').addEventListener('click', deleteDemandRow);
});

// Удаление строки из таблицы заказа
function deleteDemandRow(e) {
    const row = e.target.closest('tr');
    const table = document.querySelector('.demand tbody');
    const rows = table.querySelectorAll('tr');
    
    // Не удаляем, если это последняя строка
    if (rows.length > 1) {
        row.remove();
        renameDemandInputs();
    }
}

// Очистка таблицы заказа
document.querySelector('.remove-demand').addEventListener('click', function() {
    const table = document.querySelector('.demand tbody');
    const rows = table.querySelectorAll('tr');
    
    // Удаляем все строки кроме первой
    for (let i = rows.length - 1; i > 0; i--) {
        rows[i].remove();
    }
    
    // Очищаем значения в первой строке
    const firstRow = table.querySelector('tr');
    firstRow.querySelector('input[name^="demand_len"]').value = '';
    firstRow.querySelector('input[name^="demand_qty"]').value = '';
    
    renameDemandInputs();
});

// Переименование inputs в таблице заказа
function renameDemandInputs() {
    const table = document.querySelector('.demand tbody');
    const rows = table.querySelectorAll('tr');
    
    rows.forEach((row, index) => {
        const rowNum = index + 1;
        const lenInput = row.querySelector('input[name^="demand_len"]');
        const qtyInput = row.querySelector('input[name^="demand_qty"]');
        
        if (lenInput) lenInput.name = `demand_len${rowNum}`;
        if (qtyInput) qtyInput.name = `demand_qty${rowNum}`;
    });
}

// Инициализация обработчиков для существующих кнопок удаления
document.querySelectorAll('.delete-stock-row').forEach(button => {
    button.addEventListener('click', deleteStockRow);
});

document.querySelectorAll('.delete-demand-row').forEach(button => {
    button.addEventListener('click', deleteDemandRow);
});