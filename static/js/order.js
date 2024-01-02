function submitFormData(){
    console.log('Payment button clicked');

    var userFormData = {
        'name':null,
        'email':null,
        'total':total,
    }

    var shippingInfo = {
        'address':null,
        'area':null,
        'city':null,
        'state':null,
        'pincode':null,
    }

    if(shipping != 'False'){
        shippingInfo.address = form.address.value
        shippingInfo.area = form.area.value
        shippingInfo.city = form.city.value
        shippingInfo.state = form.state.value
        shippingInfo.pincode = form.pincode.value
    }

    if(user == 'AnonymousUser'){
        userFormData.name = form.name.value
        userFormData.email = form.email.value
    }

    var url = '/process_order/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'form': userFormData, 'shipping': shippingInfo})
    })
    .then((response) => response.json())
    .then((data) =>{
        console.log('Success:',data);
        alert('Transaction completed');
        
        cart = {};
        console.log('Cart:',cart);
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/;samesite=None"; 

        window.location.href = "{% url 'store' %}";
    })
}