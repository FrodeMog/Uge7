// ParentComponent.js
import React from 'react';
import Add_Products from './Add_products';
import Add_Category from './Add_categories';

const ParentComponent = () => {
    return (
        <div className="container">
            <div className="row">
                <div className="col-md-6">
                    <Add_Products />
                </div>
                <div className="col-md-6">
                    <Add_Category />
                </div>
            </div>
        </div>
    );
};

export default ParentComponent;