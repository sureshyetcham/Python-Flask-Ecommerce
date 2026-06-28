$('.plus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})


$('.minus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})




$('.remove-cart').click(function(){

    var id = $(this).attr('pid').toString();
    var to_remove = $(this).closest('.cart-item');

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },

        success: function(data){

            to_remove.remove();

            $('#amount_tt').text(data.amount);
            $('#totalamount').text(data.total);

            $('#cart-count').text(data.cart_count);

            if(data.cart_count == 0){
                location.reload();
            }
        }
    });
});